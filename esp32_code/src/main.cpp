#include <Arduino.h>
#include <WiFi.h>
#include "driver/i2s.h"
#include <WiFiUdp.h>
#include <WiFiUdp.h>


//Wifi credentials
const char* ssid       = "Vin1";
const char* password   = "00000000";

//Lookup server IP and port with ipconfig
IPAddress serverIP(192, 168, 110, 219);   // PC IP
const uint16_t serverPort = 5005;

#define I2S_WS 25
#define I2S_SCK 26
#define I2S_SD_IN 33
#define I2S_SD_OUT 22
#define BUTTON_PIN 32

#define I2S_PORT I2S_NUM_0

#define SAMPLE_RATE   16000
#define I2S_BUF_SAMPLES 256

WiFiUDP udp;

//State
bool recording = false;
bool playingTTS = false;
bool waitngForServer = false;

// TTS buffer
#define TTS_BUFFER_SIZE 512
uint8_t ttsBuffer[TTS_BUFFER_SIZE];
size_t bytes_written;

#define AUDIO_RING_SIZE 8192

uint8_t audioRing[AUDIO_RING_SIZE];
volatile size_t ringWrite = 0;
volatile size_t ringRead = 0;

size_t ringAvailable() {
    if (ringWrite >= ringRead)
        return ringWrite - ringRead;
    return AUDIO_RING_SIZE - (ringRead - ringWrite);
}

void ringPush(uint8_t* data, size_t len) {
    for (size_t i = 0; i < len; i++) {
        audioRing[ringWrite++] = data[i];
        ringWrite %= AUDIO_RING_SIZE;
    }
}

void ringPop(uint8_t* out, size_t len) {
    for (size_t i = 0; i < len; i++) {
        out[i] = audioRing[ringRead++];
        ringRead %= AUDIO_RING_SIZE;
    }
}



void flushUdp() {
    while (udp.parsePacket() > 0) {
        udp.read(ttsBuffer, TTS_BUFFER_SIZE);
    }
}

void playTTS() {
    uint8_t out[512];
    unsigned long lastFeed = 0;

    ringWrite = ringRead = 0;
    i2s_zero_dma_buffer(I2S_PORT);

    while (playingTTS) {
        // --- UDP receive ---
        int packetSize = udp.parsePacket();
        if (packetSize > 0) {
            int len = udp.read(ttsBuffer, TTS_BUFFER_SIZE);

            if (len == 4 && memcmp(ttsBuffer, "STOP", 4) == 0) {
                playingTTS = false;
                break;
            }

            len &= ~1;
            ringPush(ttsBuffer, len);
        }

        // --- Timed I2S feed ---
        if (millis() - lastFeed >= 16) {
            lastFeed = millis();

            if (ringAvailable() >= 512) {
                ringPop(out, 512);
                size_t written;
                i2s_write(I2S_PORT, out, 512, &written, portMAX_DELAY);
            }
        }

        delay(1);
    }
    i2s_zero_dma_buffer(I2S_PORT);
    flushUdp();
}



// #define SOFT_GAIN 3   // 2–3 is safe

// void applyGain(int16_t* data, size_t samples) {
//   for (size_t i = 0; i < samples; i++) {
//     int32_t v = data[i] * SOFT_GAIN;
//     if (v > 32767) v = 32767;
//     if (v < -32768) v = -32768;
//     data[i] = v;
//   }
// }

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLDOWN);

  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_TX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = I2S_BUF_SAMPLES,
    .use_apll = false,
    .tx_desc_auto_clear = true
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_SD_OUT,
    .data_in_num = I2S_SD_IN
  };

  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("WiFi connected");

  udp.begin(12345); // local port

  Serial.println("Set up complete");


  Serial.printf("Free heap before UDP: %u\n", ESP.getFreeHeap());
  uint8_t test[256] = {0};
  udp.beginPacket(serverIP, serverPort);
  if (udp.write(test, 256) != 256) {
      Serial.println("Failed write");
  }
  if (udp.endPacket() != 1) {
      Serial.println("Failed endPacket");
  }
  Serial.printf("Free heap after UDP: %u\n", ESP.getFreeHeap());

}
int timeout=0;
void loop() {
  //if(waitngForServer) {
    // //Serial.println("Waiting for TTS from server...");
    // int packetSize = udp.parsePacket();
    // if (packetSize > 0) {
    //   char header[10];
    //   int len = udp.read(header, sizeof(header) - 1);
    //   if (strncmp((char*)header, "START", 5) == 0) {
    //                 Serial.println(">> START TTS received");
    //                 playingTTS = true;
    //                 waitngForServer = false;
    //             }

    // }
    // timeout++;
    // //50 seconds timeout
    // if(timeout>50000){
    //   Serial.println("Timeout waiting for server");
    //   waitngForServer=false;
    //   timeout=0;
    // }
  //}else if (playingTTS){ 
  if (playingTTS){
    Serial.println("Playing TTS");
    playTTS();
    Serial.println("TTS playback finished");
  }else{
    // Button pressed → record
    static bool lastButton = false;
    bool button = digitalRead(BUTTON_PIN);

    //Start recording
    if (button && !lastButton) {
      udp.beginPacket(serverIP, serverPort);
      udp.print("START\n");
      udp.endPacket();
      i2s_zero_dma_buffer(I2S_PORT);
      recording = true;
      Serial.println("START");
    }

    if (button && recording) {
      int16_t buffer[I2S_BUF_SAMPLES];
      size_t bytes_read;

      i2s_read(I2S_PORT, buffer, sizeof(buffer),
              &bytes_read, portMAX_DELAY);
      // i2s_write(I2S_PORT, buffer, sizeof(buffer),
      //         &bytes_read, portMAX_DELAY);
      udp.beginPacket(serverIP, serverPort);
      udp.write((uint8_t*)buffer, bytes_read);;
      udp.endPacket();
    }
    //Stop recording
    if (!button && lastButton && recording) {
      udp.beginPacket(serverIP, serverPort);
      udp.print("STOP\n");
      udp.endPacket();
      recording = false;
      //waitngForServer = true;
      flushUdp();
      i2s_zero_dma_buffer(I2S_PORT);
      playingTTS = true;
      Serial.println("STOP");
    }

    lastButton = button;
  }
}
