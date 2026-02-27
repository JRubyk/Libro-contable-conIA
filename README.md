# 🤖 Libro Contable con Bot de Telegram

Proyecto experimental orientado a registrar ingresos y gastos mediante un bot de Telegram, permitiendo llevar control financiero rápido desde el celular sin usar planillas ni sistemas complejos.

El objetivo es demostrar la integración entre automatización, Python y APIs externas aplicadas a un caso real de productividad personal o para microemprendimientos.

---

## 🧰 Tecnologías utilizadas

- Python
- Telegram Bot API
- Base de datos local (SQLite)
- Variables de entorno (.env)

---

## ⚙️ Funcionamiento

El usuario envía un mensaje al bot →  
El sistema interpreta el movimiento →  
Se guarda en la base de datos →  
Luego puede consultarse o exportarse.

---

## 🚀 Cómo usar el proyecto

### 1. Clonar repositorio

```bash
git clone <url-del-repo>
cd libro-contable
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```
Activar:
```bash
venv\Scripts\activate
```

###3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 🔐 Configurar tu propio bot de Telegram
1. En Telegram abre @BotFather

2. Ejecuta:
```
/newbot
```

3. Sigue los pasos y copia el token que te entrega.
4. En el proyecto crea un archivo llamado .env

5. Dentro escribe:
```
BOT_TOKEN=TU_TOKEN_AQUI
```
6. Guarda el archivo.

---
## ▶️ Ejecutar el bot
```
python main.py
```
Si el token es correcto, el bot quedará activo y listo para recibir mensajes.
---

## 📁 Estructura general
```
libro-contable/
│
├── main.py
├── database.py
├── data/
├── .env.example
└── README.md
```

## 📚 Aprendizajes del proyecto
- Integración con APIs externas
- Automatización de tareas reales
- Manejo de persistencia de datos
- Uso de variables de entorno
- Diseño de herramientas prácticas

## 📌 Estado del proyecto
🧪 Experimental / Open Source

Se puede extender con:
- Reportes mensuales
- Exportación a Excel
- Dashboard web
- Clasificación automática de gastos

## ✍️ Autor
Proyecto creado por Jeimy Cáceres Rubio
Como experimento de automatización financiera con Python.