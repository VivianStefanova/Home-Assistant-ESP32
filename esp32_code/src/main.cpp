#include <Arduino.h>
#include "driver/i2s.h"

#define I2S_WS 25
#define I2S_SCK 26
#define I2S_SD_IN 33
#define I2S_SD_OUT 22
#define BUTTON_PIN 32

#define I2S_PORT I2S_NUM_0
#define BUFFER_SIZE 1024

int16_t buffer[BUFFER_SIZE];      // temporary buffer
int16_t audioData[16000*2];       // 2 seconds @16kHz
size_t audioIndex = 0;

#define SOFT_GAIN 3   // 2–3 is safe

void applyGain(int16_t* data, size_t samples) {
  for (size_t i = 0; i < samples; i++) {
    int32_t v = data[i] * SOFT_GAIN;
    if (v > 32767) v = 32767;
    if (v < -32768) v = -32768;
    data[i] = v;
  }
}

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
    .dma_buf_count = 4,
    .dma_buf_len = BUFFER_SIZE,
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
}

void loop() {
  // Button pressed → record
  if (digitalRead(BUTTON_PIN) == HIGH) {
    Serial.println("Button pressed");
    size_t bytes_read;
    i2s_read(I2S_PORT, buffer, sizeof(buffer), &bytes_read, portMAX_DELAY);
    for (size_t i = 0; i < bytes_read / 2 && audioIndex < sizeof(audioData)/2; i++) {
      audioData[audioIndex++] = buffer[i];
    }
  }
  // Button released → play
  else if (audioIndex > 0) {
    size_t bytes_written;
    delay(100);
    applyGain(audioData, audioIndex);
    i2s_write(I2S_PORT, audioData, audioIndex*2, &bytes_written, portMAX_DELAY);
    audioIndex = 0; // reset for next recording
  }
}
