# Dashboard del Edificio Inteligente IoT

Frontend desarrollado con React y Vite para visualizar lecturas de sensores,
estado global, actuadores, resultados ARM64 e historiales del proyecto.

## Ejecutar con datos simulados

```bash
cd EdificioIoT_ARM64/frontend
cp .env.example .env
npm install
npm run dev
```

El archivo `.env.example` viene configurado con `VITE_USE_MOCK_DATA=true`, por
lo que el dashboard puede desarrollarse sin conectar todavía la Raspberry Pi.

## Conectar con EMQX

En `.env` cambia:

```env
VITE_USE_MOCK_DATA=false
VITE_MQTT_URL=wss://TU_HOST_EMQX:8084/mqtt
VITE_MQTT_USERNAME=TU_USUARIO_DASHBOARD
VITE_MQTT_PASSWORD=TU_PASSWORD_DASHBOARD
```

El navegador se conecta mediante MQTT sobre WebSocket seguro. Los datos en
tiempo real utilizan exactamente los topics declarados en `backend/config.py`.

## Contrato de comandos

Todos los controles publican JSON en `edificio/control/remoto`:

```json
{"action":"abrir_puerta"}
{"action":"cerrar_puerta"}
{"action":"toggle_luces","value":true}
{"action":"set_modo_iluminacion","value":"AUTOMATICO"}
{"action":"toggle_ventilador","value":false}
{"action":"silenciar_alarma"}
{"action":"resetear_alerta"}
```

## Comandos disponibles

```bash
npm run dev
npm run lint
npm run build
```

No se debe subir `.env` al repositorio. Solamente se conserva
`.env.example` sin credenciales reales.
