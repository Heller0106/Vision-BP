import cv2
import numpy as np
import time
import os  # Toegevoegd voor mapbeheer

print("OpenCV versie:", cv2.__version__)
print("Probeer webcam te openen...")

# --- SETUP ---
# Maak screenshot map aan als deze nog niet bestaat
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')
    print("Map 'screenshots' aangemaakt.")

cap = None
working_index = -1

# Probeer camera indices
for index in [0, 1, 2]:
    print(f"\nProbeer camera index {index}...")
    test_cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    time.sleep(1)
    
    if test_cap.isOpened():
        ret, test_frame = test_cap.read()
        if ret and test_frame is not None:
            print(f"  ✓ Camera {index} werkt! Frame grootte: {test_frame.shape}")
            cap = test_cap
            working_index = index
            break
        else:
            print(f"  ✗ Camera {index} geeft geen beeld")
            test_cap.release()
    else:
        print(f"  ✗ Camera {index} niet beschikbaar")
        test_cap.release()

if cap is None or not cap.isOpened():
    print("\nError: Geen werkende webcam gevonden.")
    input("Druk op Enter om af te sluiten...")
    exit()

# Camera instellingen
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Warm-up routine
print(f"\nWebcam {working_index} succesvol geopend! Warming up...")
for i in range(15):  # Iets kortere warmup is vaak genoeg
    cap.read()
    time.sleep(0.05)

print("\n--- BEDIENING ---")
print("'q': Stoppen")
print("'g': Grijswaarden | 'c': Kleur")
print("'e': Edge Detection (Rood)")
print("'b': Blur")
print("'m'/'n'/'o': Spiegelen")
print("'s': Screenshot maken")
print("-----------------")

mode = 'color'
prev_time = 0  # Variabele voor FPS berekening

# --- MAIN LOOP ---
while True:
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print("Fout bij lezen frame - herstarten...")
        time.sleep(0.5)
        continue
    
    # 1. FPS Berekening (Real-time performance meting)
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time > 0 else 0
    prev_time = curr_time

    # 2. Beeldverwerking
    if mode == 'gray':
        processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
        label = "Grijswaarden"
        
    elif mode == 'edge':
        # Conversie & Blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny Detectie
        edges = cv2.Canny(blurred, 50, 150)
        
        # VERBETERING: Dikkere lijnen maken met een kernel
        kernel = np.ones((3, 3), np.uint8)  # Pas (3,3) aan naar (5,5) voor nog dikkere lijnen
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Rood masker maken
        red_edges = np.zeros_like(frame)
        red_edges[edges > 0] = [0, 0, 255] # BGR: Rood
        
        # Samenvoegen: Origineel iets donkerder (0.8), Randen fel (1.0)
        processed_frame = cv2.addWeighted(frame, 0.8, red_edges, 1.0, 0)
        label = "Rode Edge Detection"
        
    elif mode == 'blur':
        processed_frame = cv2.GaussianBlur(frame, (15, 15), 0)
        label = "Blur Effect"
        
    elif mode == 'mirror horizontal':
        processed_frame = cv2.flip(frame, 1)
        label = "Spiegel Horizontaal"
        
    elif mode == 'mirror vertical':
        processed_frame = cv2.flip(frame, 0)
        label = "Spiegel Verticaal"
    
    elif mode == 'mirror both':
        processed_frame = cv2.flip(frame, -1)
        label = "Spiegel Beide"
        
    else: # color
        processed_frame = frame.copy()
        label = "Origineel"
    
    # 3. Informatie op scherm tonen
    # Label
    cv2.putText(processed_frame, label, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # FPS en Resolutie (Dynamisch)
    info_text = f"{frame.shape[1]}x{frame.shape[0]} | FPS: {int(fps)}"
    cv2.putText(processed_frame, info_text, (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    cv2.imshow('OpenCV Webcam Analyse', processed_frame)
    
    # 4. Toetsenbord input
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('g'): mode = 'gray'
    elif key == ord('c'): mode = 'color'
    elif key == ord('e'): mode = 'edge'
    elif key == ord('b'): mode = 'blur'
    elif key == ord('m'): mode = 'mirror horizontal'
    elif key == ord('n'): mode = 'mirror vertical'
    elif key == ord('o'): mode = 'mirror both'
    elif key == ord('s'):
        # VERBETERING: Opslaan in de map
        timestamp = int(time.time())
        filename = f"screenshots/screen_{timestamp}.jpg"
        cv2.imwrite(filename, processed_frame)
        print(f"Screenshot opgeslagen: {filename}")

cap.release()
cv2.destroyAllWindows()
print("Programma afgesloten.")