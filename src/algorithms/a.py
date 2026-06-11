import pygame
import math
from typing import Tuple

# ---------------------------------------------------------------------------
# Palette : une couleur par drone (cyclique)
# ---------------------------------------------------------------------------
DRONE_COLORS = [
    (100, 180, 255),  # bleu ciel
    (120, 230, 140),  # vert menthe
    (255, 160, 80),  # orange
    (220, 100, 220),  # violet
    (255, 220, 60),  # jaune
    (100, 220, 210),  # turquoise
    (255, 120, 120),  # rouge corail
    (160, 200, 255),  # bleu pâle
]

CELL = 60  # taille d'une cellule en pixels
MARGIN = 10  # décalage du coin supérieur gauche de la grille


def grid_to_px(gx: int, gy: int) -> Tuple[float, float]:
    """Centre pixel d'une case de la grille."""
    return (MARGIN + gx * CELL + CELL // 2, MARGIN + gy * CELL + CELL // 2)


# ---------------------------------------------------------------------------
# Fonction de dessin du sprite drone (pur pygame, pas d'image externe)
# ---------------------------------------------------------------------------
def _draw_drone_shape(
    surface: pygame.Surface,
    cx: float,
    cy: float,
    color: Tuple[int, int, int],
    angle: float = 0.0,
    scale: float = 1.0,
):
    """
    Dessine un drone stylisé centré en (cx, cy).
    angle  : orientation en degrés (0 = vers le haut)
    scale  : 1.0 = taille normale
    """
    r = math.radians(angle)

    def rot(dx, dy):
        """Rotation 2D + translation vers le centre."""
        rx = dx * math.cos(r) - dy * math.sin(r)
        ry = dx * math.sin(r) + dy * math.cos(r)
        return (cx + rx * scale, cy + ry * scale)

    # Corps central (hexagone aplati)
    body_pts = [
        rot(x, y)
        for x, y in [
            (-8, 0),
            (-5, -5),
            (5, -5),
            (8, 0),
            (5, 5),
            (-5, 5),
        ]
    ]
    pygame.draw.polygon(surface, color, body_pts)
    pygame.draw.polygon(surface, (255, 255, 255), body_pts, 1)

    # Croix des bras
    arm_color = tuple(max(0, c - 40) for c in color)
    for dx, dy in [(14, 0), (-14, 0), (0, 14), (0, -14)]:
        ax, ay = rot(dx * 0.55, dy * 0.55)
        pygame.draw.line(
            surface, arm_color, (cx, cy), (ax, ay), max(1, int(2 * scale))
        )

    # Rotors (4 cercles aux extrémités des bras)
    rotor_color = tuple(min(255, c + 60) for c in color)
    for dx, dy in [(14, 0), (-14, 0), (0, 14), (0, -14)]:
        rx, ry = rot(dx, dy)
        pygame.draw.circle(
            surface, rotor_color, (int(rx), int(ry)), max(2, int(5 * scale))
        )
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(rx), int(ry)),
            max(2, int(5 * scale)),
            1,
        )

    # Lumière centrale (indicateur couleur vif)
    light = tuple(min(255, c + 80) for c in color)
    pygame.draw.circle(
        surface, light, (int(cx), int(cy)), max(2, int(3 * scale))
    )


# ---------------------------------------------------------------------------
# Classe principale DroneSprite
# ---------------------------------------------------------------------------
class DroneSprite:
    """
    Représentation visuelle d'un drone sur la grille MAPF.

    Paramètres
    ----------
    drone_id   : identifiant unique (int), détermine la couleur
    position   : case initiale (col, row) dans la grille
    sprite     : 'default' | une Surface pygame personnalisée (facultatif)
    anim_speed : durée d'une animation move_to en secondes
    """

    def __init__(
        self,
        drone_id: int,
        position: Tuple[int, int],
        sprite: "pygame.Surface | str" = "default",
        anim_speed: float = 0.25,
    ):

        self.drone_id = drone_id
        self.grid_pos: Tuple[int, int] = position
        self.color = DRONE_COLORS[drone_id % len(DRONE_COLORS)]
        self.anim_speed = anim_speed  # secondes pour traverser une case

        # Position pixel courante (float pour interpolation douce)
        px, py = grid_to_px(*position)
        self.px: float = px
        self.py: float = py

        # État de l'animation
        self._anim_active: bool = False
        self._anim_start: Tuple[float, float] = (px, py)
        self._anim_end: Tuple[float, float] = (px, py)
        self._anim_elapsed: float = 0.0
        self._angle: float = 0.0

        # Sprite personnalisé ou dessin procédural
        if isinstance(sprite, pygame.Surface):
            self._custom_sprite: "pygame.Surface | None" = sprite
        else:
            self._custom_sprite = None  # utilise _draw_drone_shape

    # ------------------------------------------------------------------
    # Propriété publique position (met à jour px/py si on la change sans animation)
    # ------------------------------------------------------------------
    @property
    def position(self) -> Tuple[int, int]:
        return self.grid_pos

    @position.setter
    def position(self, new_pos: Tuple[int, int]):
        self.grid_pos = new_pos
        self.px, self.py = grid_to_px(*new_pos)
        self._anim_active = False

    # ------------------------------------------------------------------
    # move_to : démarre l'animation vers une case destination
    # ------------------------------------------------------------------
    def move_to(self, dest: Tuple[int, int]):
        """
        Lance une animation de la position courante vers `dest`.
        L'appel est non-bloquant ; appelé update() chaque frame pour progresser.
        """
        if dest == self.grid_pos and not self._anim_active:
            return  # rien à faire

        # Calcul de l'angle de déplacement (pour orienter le sprite)
        dx = dest[0] - self.grid_pos[0]
        dy = dest[1] - self.grid_pos[1]
        if dx != 0 or dy != 0:
            self._angle = math.degrees(math.atan2(dx, -dy))  # 0° = haut

        self._anim_start = (self.px, self.py)
        self._anim_end = grid_to_px(*dest)
        self._anim_elapsed = 0.0
        self._anim_active = True
        self.grid_pos = dest  # mise à jour logique immédiate

    # ------------------------------------------------------------------
    # update : appelé chaque frame avec le delta-temps (secondes)
    # ------------------------------------------------------------------
    def update(self, dt: float):
        """Avance l'animation si elle est en cours."""
        if not self._anim_active:
            return

        self._anim_elapsed += dt
        t = min(self._anim_elapsed / self.anim_speed, 1.0)
        t = _ease_in_out(t)

        sx, sy = self._anim_start
        ex, ey = self._anim_end
        self.px = sx + (ex - sx) * t
        self.py = sy + (ey - sy) * t

        if self._anim_elapsed >= self.anim_speed:
            self.px, self.py = self._anim_end
            self._anim_active = False

    @property
    def is_moving(self) -> bool:
        return self._anim_active

    # ------------------------------------------------------------------
    # draw : rendu sur la surface cible
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        """Dessine le drone à sa position pixel courante."""
        if self._custom_sprite is not None:
            w, h = self._custom_sprite.get_size()
            surface.blit(
                self._custom_sprite,
                (int(self.px - w // 2), int(self.py - h // 2)),
            )
        else:
            # Légère pulsation de taille pendant le déplacement
            scale = 1.1 if self._anim_active else 1.0
            _draw_drone_shape(
                surface, self.px, self.py, self.color, self._angle, scale
            )

        # Numéro du drone
        if not hasattr(DroneSprite, "_font_cache"):
            DroneSprite._font_cache = {}
        font = DroneSprite._font_cache.setdefault(
            12, pygame.font.SysFont("monospace", 12, bold=True)
        )
        label = font.render(str(self.drone_id), True, (255, 255, 255))
        surface.blit(
            label,
            (
                int(self.px - label.get_width() // 2),
                int(self.py - label.get_height() // 2),
            ),
        )

    # ------------------------------------------------------------------
    # draw_trail : trace fantôme de la trajectoire (facultatif)
    # ------------------------------------------------------------------
    def draw_trail(
        self, surface: pygame.Surface, path: list, current_turn: int
    ):
        """
        Dessine les cases déjà visitées en semi-transparent.
        path        : list[(col, row)] pour ce drone
        current_turn: index du tour actuel
        """
        for i in range(1, min(current_turn + 1, len(path))):
            x1, y1 = grid_to_px(*path[i - 1])
            x2, y2 = grid_to_px(*path[i])
            alpha_surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            r, g, b = self.color
            pygame.draw.line(
                alpha_surf,
                (r, g, b, 60),
                (CELL // 2, CELL // 2),
                (CELL // 2, CELL // 2),
                1,
            )
            pygame.draw.line(
                surface,
                (*self.color, 80),
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                2,
            )


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------
def _ease_in_out(t: float) -> float:
    """Courbe ease-in-out cubique (0 → 1)."""
    return t * t * (3 - 2 * t)


def create_drones(starts: list, anim_speed: float = 0.25) -> list:
    """
    Crée une liste de DroneSprite à partir des positions de départ.

    Exemple
    -------
    drones = create_drones([(0,0), (1,0), (2,0)])
    """
    return [
        DroneSprite(i, pos, anim_speed=anim_speed)
        for i, pos in enumerate(starts)
    ]


# ---------------------------------------------------------------------------
# Demo standalone (python drone_sprite.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    pygame.init()
    W, H = 7 * CELL + 2 * MARGIN, 7 * CELL + 2 * MARGIN + 60
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("DroneSprite — demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 13)

    # 3 drones avec des chemins pré-définis
    PATHS = [
        [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)],
        [(0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (4, 4)],
        [(3, 6), (3, 5), (3, 4), (3, 3), (3, 2), (3, 1), (3, 0)],
    ]
    drones = [
        DroneSprite(i, p[0], anim_speed=0.3) for i, p in enumerate(PATHS)
    ]
    turn = 0
    total = max(len(p) for p in PATHS)
    moving = False

    def advance_turn():
        global turn, moving
        if turn < total - 1:
            turn += 1
            for i, d in enumerate(drones):
                if turn < len(PATHS[i]):
                    d.move_to(PATHS[i][turn])
            moving = True

    def draw_grid():
        for col in range(7):
            for row in range(7):
                rect = pygame.Rect(
                    MARGIN + col * CELL, MARGIN + row * CELL, CELL, CELL
                )
                pygame.draw.rect(screen, (40, 40, 40), rect)
                pygame.draw.rect(screen, (65, 65, 65), rect, 1)

    running = True
    auto = False
    auto_timer = 0.0

    while running:
        dt = clock.tick(60) / 1000.0
        auto_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    advance_turn()
                if event.key == pygame.K_r:
                    auto = not auto

        if auto and auto_timer > 0.45:
            auto_timer = 0.0
            advance_turn()

        any_moving = any(d.is_moving for d in drones)
        for d in drones:
            d.update(dt)

        screen.fill((20, 20, 20))
        draw_grid()
        for i, d in enumerate(drones):
            d.draw_trail(screen, PATHS[i], turn)
        for d in drones:
            d.draw(screen)

        # HUD
        step_col = (80, 150, 220)
        run_col = (60, 180, 100) if auto else (80, 80, 80)
        step_r = pygame.draw.rect(
            screen, step_col, (10, H - 50, 130, 36), border_radius=6
        )
        run_r = pygame.draw.rect(
            screen, run_col, (150, H - 50, 130, 36), border_radius=6
        )
        screen.blit(
            font.render("→ Next step [SPC]", True, (255, 255, 255)),
            (18, H - 38),
        )
        screen.blit(
            font.render("▶ Auto run  [R]", True, (255, 255, 255)),
            (158, H - 38),
        )
        screen.blit(
            font.render(f"Tour {turn}/{total-1}", True, (180, 180, 180)),
            (300, H - 38),
        )

        if pygame.mouse.get_pressed()[0]:
            mp = pygame.mouse.get_pos()
            if step_r.collidepoint(mp):
                advance_turn()
            if run_r.collidepoint(mp):
                auto = not auto

        pygame.display.flip()

    pygame.quit()
