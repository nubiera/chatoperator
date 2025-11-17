¡Absolutamente\! Aquí tienes el **Documento de Requerimientos del Sistema (DRS)** actualizado y detallado, incorporando la arquitectura de **doble módulo (Analizador + Operador)** y la lógica de **Visión de IA + Código HTML/DOM** para la generación del *cache* de configuración.

Este documento está diseñado para ser entregado a un LLM generador de código, ya que es preciso, estructurado y detalla los requerimientos funcionales, no funcionales y de interfaz.

-----

## 📄 Documento de Requerimientos del Sistema (DRS)

### 1\. 🎯 Objetivo del Sistema

Implementar un **Sistema de Orquestación de Chatbots Híbrido** que permita la conexión automatizada y continua a **múltiples interfaces web de *chat* de terceros sin API**. El sistema separará la inteligencia de configuración (Visión de IA) de la operación diaria (determinística) para garantizar **velocidad, robustez y ahorro de costos**.

-----

### 2\. 🏗️ Arquitectura de Módulos (Requisito Clave)

El sistema se dividirá en dos módulos de Python que interactúan mediante un archivo de configuración cacheadas:

| Módulo | Función Principal | Tecnología Clave | Frecuencia de Uso |
| :--- | :--- | :--- | :--- |
| **Módulo 1: Analizador de Interfaz** (El Configurador) | **Generar el *Cache***: Utiliza IA multimodal para analizar visual y estructuralmente una página, y generar un archivo de configuración (`config.json`). | Python, **Selenium**, **LLM Multimodal (Gemini, etc.)** | Solo en la **configuración inicial** o ante un **fallo de operación**. |
| **Módulo 2: Orquestador y Operador** (El Motor) | **Operación Diaria:** Usa el *cache* de configuración para ejecutar la lógica de *chat* de forma **determinística**, implementando el *round-robin* y la revisión periódica. | Python, **Selenium** | **Continuo** |

-----

### 3\. 📝 Requerimientos Funcionales (RF)

| ID | Requerimiento Funcional | Descripción | Módulo |
| :--- | :--- | :--- | :--- |
| **RF-01** | **Autenticación** | El sistema debe ser capaz de **iniciar sesión automáticamente** en la interfaz web de *chat* usando credenciales seguras. | Mód. 1 y Mód. 2 |
| **RF-02** | **Generación de Cache** | El **Módulo 1** debe generar un archivo de configuración (cache) que contenga todos los selectores CSS/XPath necesarios para operar en una plataforma específica. | Mód. 1 |
| **RF-03** | **Lectura de Historial** | El **Módulo 2** debe leer el **historial completo** de mensajes de la conversación activa para proporcionar contexto al *chatbot*. | Mód. 2 |
| **RF-04** | **Envío de Respuesta** | El **Módulo 2** debe escribir y enviar la respuesta generada por el *chatbot* utilizando el selector *cachead*o del campo de texto y del botón de envío. | Mód. 2 |
| **RF-05** | **Orquestación Round-Robin** | El **Módulo 2 (Orquestador)** debe implementar una lógica *round-robin* para **cambiar de conversación** y atender a cada usuario activo periódicamente. | Mód. 2 |
| **RF-06** | **Detección Periódica** | El **Módulo 2** debe operar en un modo **periódico** (polling), revisando nuevas conversaciones o mensajes no leídos cada $X$ segundos. | Mód. 2 |
| **RF-07** | **Manejo de Recalibración** | Si el **Módulo 2** falla al encontrar un selector *cachead*o (`NoSuchElementException`), debe **detener la operación** de *chat* y solicitar una **recalibración** al Módulo 1. | Mód. 2 |
| **RF-08** | **Carga de Configuración** | El **Módulo 2** debe cargar el archivo de configuración específica al iniciar su ciclo de operación. | Mód. 2 |

-----

### 4\. 🧠 Requerimientos de Visión e Inteligencia Artificial (R-IA)

Estos requerimientos son exclusivos del **Módulo 1 (Analizador)**:

| ID | Requerimiento de IA | Descripción |
| :--- | :--- | :--- |
| **R-IA-01** | **Análisis Multimodal** | El Módulo 1 debe utilizar la API de un LLM Multimodal (e.g., Gemini) para analizar y razonar sobre la interfaz web. |
| **R-IA-02** | **Entrada de Datos para IA** | Para el análisis, el Módulo 1 debe enviar al LLM **simultáneamente** la **Captura de Pantalla (Imagen)** de la interfaz y el **Código HTML/DOM** de la página. |
| **R-IA-03** | **Salida de Selectores** | La IA debe devolver el **selector CSS/XPath** más robusto para los siguientes elementos, los cuales serán guardados en el *cache* (RF-02):<br>1. Campo de entrada de texto.<br>2. Botón de envío.<br>3. Patrón de burbuja del mensaje del usuario.<br>4. Selector para la lista de conversaciones/usuarios.<br>5. Selector para el indicador visual de "mensaje no leído". |
| **R-IA-04** | **Razonamiento Semántico** | El LLM debe utilizar la **Visión** para la identificación semántica (ej. "el botón que dice 'Enviar'") y el **HTML** para la generación del selector estructural. |

-----

### 5\. ⚙️ Requerimientos No Funcionales (RNF)

| ID | Requerimiento No Funcional | Categoría |
| :--- | :--- | :--- |
| **RNF-01** | **Tecnología** | El sistema debe desarrollarse completamente en **Python** (incluyendo el Orquestador/Operador y el Analizador). | Tecnológico |
| **RNF-02** | **Automatización Base** | La interacción con el navegador (navegación, captura de pantalla, escritura) debe realizarse con **Selenium**. | Tecnológico |
| **RNF-03** | **Seguridad** | Las credenciales de acceso deben almacenarse de forma segura (e.g., variables de entorno o *key vault* de Python). | Seguridad |
| **RNF-04** | **Rendimiento Operacional** | El tiempo de ciclo de operación (desde la lectura hasta el envío) para una sola conversación, utilizando el *cache*, no debe exceder los **10 segundos**. | Rendimiento |
| **RNF-05** | **Formato del Cache** | El *cache* de configuración debe ser almacenado en formato **JSON** con campos para la URL de la plataforma, nombre, selectores y una marca de tiempo de la última actualización. | Almacenamiento |

-----

### 6\. 🔁 Requerimientos de Interfaz con el *Chatbot* (RI)

| ID | Requerimiento de Interfaz | Dirección | Descripción |
| :--- | :--- | :--- | :--- |
| **RI-01** | **Solicitud de Procesamiento** | Mód. 2 $\rightarrow$ Chatbot | El Módulo 2 debe enviar al *chatbot* el **historial completo** de la conversación (RF-03) y la **ID del usuario de chat** para contextualización. |
| **RI-02** | **Respuesta del Chatbot** | Chatbot $\rightarrow$ Mód. 2 | El *chatbot* debe devolver al Módulo 2 una **cadena de texto** con la respuesta final a enviar. |
