# Module

- Kamera-Server ```tdi-camera.py```
   - automatische Steuerung der Kamera
   - Bsp.: ```python tdi-camera.py --start```
   - Parameter
      - ```--start``` Starten des Servers
      
- Steuerpgrogramm ```tdi-control.py```
  - Durchführung einer Messung und anschließendes kopieren der Dateien auf ein gemeinsames Netzlaufwerk.
  - Bsp.: ```python tdi-control.py --task=speed-ratio --name="Speed Ratio Messung"```
  - Parameter
    - ```--task=[TASK-FILE]``` Parameter-Datei im JSON Format
    - ```--name=[NAME]``` Name des Ordners (in dem die Messdateien abgespeichert werden)
    - ```--show-config``` Alle Konfigurationsparameter anzeigen
    - ```--test``` Testlauf ausführen
    - ```--reboot``` XPS neustarten
    
- Task-Generator ```tdi-json.py```
  - Hilfsprogramm zum Bauen der Parameterdateien
  - Script muss in der Regel angepasst werden um die genauen Bedingungen für die einzelnen Messdurchläufe zu erzeugen. Bei Speed-Ratio-Messung: Start Speed-Ratio/Stop Speed-Ratio/Iterationen/Schrittweite.
  - Bsp.: ```python tdi-repair.py --mtf```
  - Parameter
    - ```--test``` Parameterdatei für den Testlauf erstelen
    - ```--mtf``` Parameterdatei für MTF-Messungen erzeugen
    - ```--speed-ratio``` Parameterdatei für Speed-Ratio-Messungen erzeugen
    - ```--repair=[FOLDER]``` Parameterdatei für unfertige Messungen (Spot/Gatherdatei zu klein) erzeugen
    - ```--focus``` Parameterdatei für Fokuskalibrierung erzeugen
    
- Visualisierungsprogramm ```tdi-view.py```
  - Visualisierung der Messergebnisse mittels matplotlib
  - Bsp.: ```python tdi-view.py --plot=speed-ratio --file="Speed Ratio Messung"```
  - Parameter
    - ```--plot=[TYPE]```
      - _gather_ Positions- und Geschwindigkeitsdaten visualisieren
      - _spot_ Helligkeitswerte visualisieren
      - _gauss_ Gaussfit des hellsten Spots visualisieren
      - _movie_ Video mehrerer Messdurchläife (Ordnername muss übergeben werden)
      - _speed-raio_ Speed-Ratio-Diagram (Ordnername muss übergeben werden) 
    - ```--file=[FILE]``` Datei oder Ordner der Messung
    - ```--save``` Ergebnisse in NumPy-Datenstrukturen gespeichert um zukünftige Berechnung zu beschleunigen. Wird benutzt um Neuberechnung zu erzwingen. Bei speed-ratio werden außerdem die statistischen Daten als csv-Datei gespeichert.

# Allgemeine Hinweise
- Der Quellcode ist auf github zu finden: https://github.com/g41nxe/dlr-tdi-py
- Zum Ausführen des Steuer/Kamera-Programms reicht python2.7 benötigt. Zum Ausführen des Auswertungsprogramms wird jedoch Python 3.x benötigt. Es empfiehlt sich die Installation der Python-Distribution Anaconda. Um Videos zu erzeugen muss außerdem ffmpeg installiert werden.
- Bricht die Ausführung eines langen Durchlaufs ab müssen ggf. Messungen wiederholt werden. Dazu kann mittels dem python ```tdi-json.py --repair=FOLDER``` versucht werden eine Reparatur-Datei zu erzeugen. Keine Garantie auf Erfolg! Reicht das nicht aus, muss die Datei manuell "zusamengebaut" werden. Vor dem Ausführen der Visualisierung müssen dann die nachträglich erzeugten .gathering und .spot Dateien umbenannt werden, sodass sie dem Namensschema der ursprünglichen Messdateien entsprechen.
- Namesschema: ```/<Datum>/<ID>/<Zeit>_<Parameterdatei-ID>_<#Durchlauf>.<spot|gather>```
- Es gibt eine globale Config-Datei die alle weiteren Einstellungen festhält ```common/config.py```. Nennenswert ist bspw. der Dateipfad für Messdateien: ```PLOT_DATA_FOLDER```. Dort sind auch die Zugangsdaten zum XPS-Controller (via FTP) gespeichert.
- Logging kann aus/ab geschaltet werden in der Config-Datei. Mögliche werte ```Logging.INFO``` (ausführlich) oder ```Logging.WARNING``` (wenig)
- Bei Speed-Ratio Messungen unterscheidet sich die Anzahl der aufgenommenen, braucharen Spotbilder je nach XMS-Geschwindigkeit. Ist das SR < 1 gibt es teilweise < 5 Bilder.
- Die Anzahl der Iterationen ist durch den XPS begrenzt. mehr als 30 Iterationen erzeugt zu große Messdateien, die vom XPS nicht verarbeitet werden können.

# Datenvisualisierung mit Matplotlib
- Die Auswertungsscripte (werden mit Matplotlib erzeugt) sind in plot/animation unterteilt und befinden sich im Ordner plot. 
- Alle Scripte implementieren (je nach Typ) von ```PlotInterface``` oder ```AnmiationInterface```. Es gibt immer 2 Funktionen: ```plot``` und ```plotDirectory```. Jenachdem ob eine einzelne Messung oder ein ganzer Ordner visualisiert werden soll.
- Plot- und Animation-Klassen mit Daten, die initial viel Rechenaufwand erfordern können von der Klasse ```NPYLoader``` erben. Es muss dann eine Funktion ```buildAndAppendData``` implementiert werden, die dafür verantwortlich ist einen NumPy-Array zu bauen, der die einzelnen Messdaten enthält. Die NumPy-Datei wird dann im selben Ordner wie die Messdaten gespeichert und mit der ID des Messdurchlaufs benannt.

# Bauen von Parameterdateien
- Parameterdateien werden im Ordner tasks/ gespeichert.
- Bsp. Fokus-Datei (Die Fokus-Kalibrierung mittels dieses Scripts hat sich nicht als sinnvoll erwiesen eignet sich aber gut zur Veranschaulichung.)
```Javascript
{
  "id": "focus",
  "desc": "Iteration entlang der Y-Achse zur Fokus-Kalibrierung",
  "runs": [
    { 
      "velocity": 81, 
      "position": [["CAM_Y_GROUP", [5.0]]], 
      "frequency": 9615,
      "config": [["ITERATIONS", 30]]
    },
    { "position": [["CAM_Y_GROUP", [5.5]]] },
    { "position": [["CAM_Y_GROUP", [6.0]]] },
    { "position": [["CAM_Y_GROUP", [6.5]]] },
    { "position": [["CAM_Y_GROUP", [7.0]]] },
    { "position": [["CAM_Y_GROUP", [7.5]]] },
    { "position": [["CAM_Y_GROUP", [8.0]]] },
    { "position": [["CAM_Y_GROUP", [8.5]]] },
    { "position": [["CAM_Y_GROUP", [9.0]]] }
  ]
}
```
- Schlüsselwörter:
  - _id_: eindeutiger, kurzer Bezeichner
  - _desc_: Beschreibung
  - _runs_: Array der einzelnen, unterschiedlichen Messdurchläufe (runs). Ein Run kann beliebig viele Eintstellunge der folgenden Parameter enthalten.:
    - _config_: hier können die Namen der Parameter in der Config-Datei übergeben werden um diee zu überschreiben.
    - _position_: Ein Array der 3-Achsen des Kamera-Positionierers (Namen der Achsen finden sich in der Config-Datei). Positionsangabe muss auch immer ein Array sein.
    - _velocity_: Geschwindigkeit
    - frequency: TDI-Frequenz

# Netzwerkommunikation
- Der Kamera-Server wartet kontinuierlich auf den Empfang von Befehlen via Socket-Schnittstelle.
- Befehle werden via Socket als String übertragen. Die Kapselung erfolgt via der Klassen Command und Repsonse. Sie beinhalten die auszufhrende Funktion, deren Parameter und ggf. Rückgabewerte. Vorangestellt ist die Länge des Befehls. 
- Aufbau von Command: 
  ```length (2) . Command.type (4-5) , value (0-16)```
  - type: ```freq```, ```start```, ```stop```, ```save```, ```test```
- Aufbau vom Response: 
  ```length (11-28) . Command.type (4-5) . value (0-16) . Response.type (7)```
  - type: ```sucess```, ```failure```
- Der empfangene Befehl wird dann auf die entsprechenden Funktionen der Klasse ``` ```

# Arbeitsablauf
1. Alle Geräte anschalten
2. Kalibrierung
3. Kamera-Server auf dem Kamera-PC starten
4. ggf. Paramaterdatei erzeugen 
5. ggf. Remote-Desktop-Verbindungen herstellen (erfordert entspr. Rechte)
6. Stuerprogramm unter Angabe der Parameterdatei und Namen des Messdurchlaufs starten
7. Warten.
8. Daten ggf. auf den Auswertungs-PC kopieren (Remote Desktop Verbindung, USB-Stick)
9. Auswertungsprogramm unter Angabe der Messdaten (bzw. des Ordners der die Messdaten enthält) und des Plot-Typs starten