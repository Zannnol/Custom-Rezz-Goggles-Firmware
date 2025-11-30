# Fichier: code.py (Spirale Hypnotique avec pulse)

from random import random
import board
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
from time import monotonic
import math

# --- 1. CONFIGURATION DES CONSTANTES ---
BRIGHTNESS_MAX = 0.5   # Luminosité (ajustez entre 0.0 et 1.0)
LED_COUNT = 88
PIN = board.D5

# Paramètres fixes pour la spirale
FIXED_SPEED = 1.0   # Vitesse de rotation (augmentez pour plus rapide)
HUE_STEP = 0.0    # Vitesse du cycle de couleur (0.003 est lent et doux)
MODE_MIRROR = 1     # 1 = Effet miroir actif (pour une spirale symétrique)
RING_SWITCH_TIME = 2 # Durée de fondu en secondes entre les changements d'anneaux

# Déclare l'objet NeoPixel
PIXELS = neopixel.NeoPixel(
    PIN, LED_COUNT, auto_write=False, brightness=1.0, pixel_order=neopixel.RGB
)

# Initialisation des positions et de la couleur (aléatoire juste au démarrage)
HUE = 0.0              
MIDDLE_POS = random() * 144 
POS = random() * 144       

# Variables de contrôle du rebond et du fondu
ring_mode = 0                   # Anneau entrant (fading IN)
previous_ring_mode = 2          # Anneau sortant (fainding OUT)
last_switch_time = monotonic()
direction = 1 # 1 pour avancer (0->1->2), -1 pour reculer (2->1->0)

# --- 2. PRÉ-CALCULS DES OFFSETS ---
# Ceci définit la structure des anneaux. Ne pas modifier.
MIRROR_X = []
OFFSET_OUTER = []
OFFSET_MIDDLE = []
OFFSET_INNER = []

for i in range(24):
    MIRROR_X.append(67 - ((i + 11) % 24))
    OFFSET_OUTER.append(i * 6)
for i in range(16):
    MIRROR_X.append(83 - ((i + 7) % 16))
    OFFSET_MIDDLE.append(i * 9)
for i in range(4):
    MIRROR_X.append(87 - ((i + 2) % 4))
    OFFSET_INNER.append(i * 36)

def set_pixel(index, color):
    """Définit la couleur d'un pixel dans les deux yeux avec le miroir actif."""
    PIXELS[index] = color
    if MODE_MIRROR:
        PIXELS[MIRROR_X[index]] = color
    else:
        PIXELS[44 + index] = color

# --- 3. BOUCLE PRINCIPALE D'ANIMATION (FONDU ENCHAINE) ---
while True:
    NOW = monotonic()

    # 1. Calcul du facteur linéaire de fondu (0.0 à 1.0)
    linear_fade_factor = (NOW - last_switch_time) / RING_SWITCH_TIME

    # Normaliser la progression pour que le fondu soit plus doux
    eased_factor = 0.5 - 0.5 * math.cos(linear_fade_factor * math.pi)

    # 2. Gestion de l'était (quand le fondu est terminé)
    if linear_fade_factor >= 1.0:
        # L'anneau courrant devient le précédent
        previous_ring_mode = ring_mode

        # Logique de rebond
        if ring_mode == 2:
            direction = -1
        elif ring_mode == 0:
            direction = 1

        ring_mode += direction          # Passe au mode suivant
        last_switch_time = NOW          # Réinitialise le temps de switch
        fade_factor = 0.0               # Assure que le fondu commence à 0.0

    # 3. Mise à jour des couleurs des deux anneaux
    # Calcul de la luminosité pour l'anneau ENTRANT (Augment de 0 à BRIGHTNESS_MAX)
    br_in = eased_factor * BRIGHTNESS_MAX
    COLOR_IN = fancy.CHSV(HUE, 1.0, br_in).pack()

    # Calcul de la luminosité pour l'anneau SORTANT (Diminue de BRIGHTNESS_MAX à 0)
    br_out = (1.0 - eased_factor) * BRIGHTNESS_MAX
    COLOR_OUT = fancy.CHSV(HUE, 1.0, br_out).pack()

    # 4. Dessine les anneaux (Rotation sélective avec fondu)
    for ring in range(3):
        # Détermine la couleur à utiliser pour cet anneau (entrant, sortant ou éteint)
        if ring == ring_mode:
            current_color = COLOR_IN
        elif ring == previous_ring_mode:
            current_color = COLOR_OUT
        else:
            current_color = 0 # Eteint

        # Anneau extérieur (24 pixels, 8 allumés) - ring 0
        if ring == 0:
            if current_color != 0:
                for i in range(24):
                    j = (POS + OFFSET_OUTER[i]) % 72
                    set_pixel(i, current_color if j < 24 else 0)
            else:
                for i in range(24): set_pixel(i, 0) # Eteint si non actif

        # Anneau du milieu (16 pixels, 6 allumés) - ring 1
        elif ring == 1:
            if current_color != 0:
                for i in range(16):
                    j = (OFFSET_MIDDLE[i] + MIDDLE_POS) % 72
                    set_pixel(24 + i, current_color if j < 27 else 0)
            else:
                for i in range(16): set_pixel(24 + i, 0) # Eteint si non actif

        # Anneau intérieur (4 pixels, 3 allumés) - ring 2
        elif ring == 2:
            if current_color != 0:
                for i in range(4):
                    j = (POS + OFFSET_INNER[i]) % 144
                    set_pixel(40 + i, current_color if j < 108 else 0)
            else:
                for i in range(4): set_pixel(40 + i, 0) # Eteint si non actif

    # Envoie les données aux LEDs
    PIXELS.show()

    # 3. Avancement continu

    # Fait tourner la couleur en permanence (cycle chromatique)
    HUE = (HUE + HUE_STEP) % 1.0 

    # Incrémente la position des trois anneaux à vitesse fixe (Rotation)
    POS = (POS + FIXED_SPEED) % 144
    MIDDLE_POS = (MIDDLE_POS - FIXED_SPEED) % 144 # L'anneau central tourne dans le même sens