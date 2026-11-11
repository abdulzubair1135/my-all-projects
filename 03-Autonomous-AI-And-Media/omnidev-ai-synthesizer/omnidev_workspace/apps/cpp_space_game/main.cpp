// Space Fighter 2D - C++ Raylib Game Engine
#include "raylib.h"
#include <vector>
#include <cstdlib>

struct Bullet { Vector2 pos; float speed; bool active; };
struct Enemy { Vector2 pos; float speed; float radius; bool active; };

int main() {
    const int screenWidth = 800;
    const int screenHeight = 600;
    InitWindow(screenWidth, screenHeight, "Space Fighter 2D");
    SetTargetFPS(60);

    Vector2 player = { screenWidth / 2.0f, screenHeight - 60.0f };
    int score = 0, shield = 100;
    std::vector<Bullet> bullets;
    std::vector<Enemy> enemies;

    while (!WindowShouldClose()) {
        // Controls
        if (IsKeyDown(KEY_LEFT) || IsKeyDown(KEY_A)) player.x -= 6.0f;
        if (IsKeyDown(KEY_RIGHT) || IsKeyDown(KEY_D)) player.x += 6.0f;
        if (IsKeyPressed(KEY_SPACE)) {
            bullets.push_back({ { player.x, player.y - 20 }, 12.0f, true });
        }

        // Spawning
        if (GetRandomValue(0, 40) == 0) {
            enemies.push_back({ { (float)GetRandomValue(30, screenWidth - 30), -20.0f }, (float)GetRandomValue(2, 4), 16.0f, true });
        }

        // Updates
        for (auto& b : bullets) b.pos.y -= b.speed;
        for (auto& e : enemies) e.pos.y += e.speed;

        BeginDrawing();
        ClearBackground(GetColor(0x030712ff));

        // Draw Player
        DrawTriangle({ player.x, player.y - 20 }, { player.x - 15, player.y + 15 }, { player.x + 15, player.y + 15 }, RAYWHITE);
        
        // Draw Bullets & Enemies
        for (auto& b : bullets) if (b.pos.y > 0) DrawRectangle(b.pos.x - 2, b.pos.y - 6, 4, 12, SKYBLUE);
        for (auto& e : enemies) if (e.pos.y < screenHeight + 20) DrawCircle(e.pos.x, e.pos.y, e.radius, RED);

        DrawText(TextFormat("SCORE: %i | SHIELD: %i%%", score, shield), 20, 20, 20, SKYBLUE);
        EndDrawing();
    }

    CloseWindow();
    return 0;
}
