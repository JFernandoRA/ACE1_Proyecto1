/*
  mq2_ldr_reader.ino

  Lee el sensor de gas MQ-2 (salida analógica AO) y el LDR (divisor de
  voltaje) y envía ambos valores por USB a la Raspberry Pi, cada 300 ms,
  en el formato exacto:

      GAS:<0-1023>,LUZ:<0-1023>

  Conexiones en el Arduino Uno:
    MQ-2   VCC -> 5V
    MQ-2   GND -> GND
    MQ-2   AO  -> A0

    LDR: divisor de voltaje
      5V -- LDR -- (A1) -- resistencia 10K -- GND
    (si tu LDR viene en módulo con pines VCC/GND/AO, conecta igual que el MQ-2
     pero AO -> A1)

  IMPORTANTE: el GND del Arduino y el GND de la Raspberry Pi quedan unidos
  automáticamente por el propio cable USB, no se necesita cable adicional.
*/

const int PIN_MQ2 = A0;
const int PIN_LDR = A1;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int gas = analogRead(PIN_MQ2);   // 0-1023
  int luz = analogRead(PIN_LDR);   // 0-1023

  Serial.print("GAS:");
  Serial.print(gas);
  Serial.print(",LUZ:");
  Serial.println(luz);

  delay(300);
}
