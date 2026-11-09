#include "API.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 64

static int getInteger(const char* command) {
    printf("%s\n", command);
    fflush(stdout);
    char response[BUFFER_SIZE];
    if (!fgets(response, sizeof(response), stdin)) {
        return 0;
    }
    return atoi(response);
}

static int getString(const char* command, char* response) {
    printf("%s\n", command);
    fflush(stdout);
    if (!fgets(response, BUFFER_SIZE, stdin)) {
        response[0] = '\0';
        return -1;
    }
    // Trim newline (\n) and carriage return (\r) if present
    size_t len = strlen(response);
    while (len > 0 && (response[len - 1] == '\n' || response[len - 1] == '\r')) {
        response[--len] = '\0';
    }
    return 0;
}

int API_mazeWidth(void) {
    return getInteger("mazeWidth");
}

int API_mazeHeight(void) {
    return getInteger("mazeHeight");
}

int API_wallFront(void) {
    char response[BUFFER_SIZE];
    getString("wallFront", response);
    return strcmp(response, "true") == 0;
}

int API_wallRight(void) {
    char response[BUFFER_SIZE];
    getString("wallRight", response);
    return strcmp(response, "true") == 0;
}

int API_wallLeft(void) {
    char response[BUFFER_SIZE];
    getString("wallLeft", response);
    return strcmp(response, "true") == 0;
}

int API_moveForward(void) {
    char response[BUFFER_SIZE];
    getString("moveForward", response);
    return strcmp(response, "ack") == 0;
}

void API_turnRight(void) {
    char response[BUFFER_SIZE];
    getString("turnRight", response);
    (void)response;
}

void API_turnLeft(void) {
    char response[BUFFER_SIZE];
    getString("turnLeft", response);
    (void)response;
}

void API_setWall(int x, int y, char direction) {
    printf("setWall %d %d %c\n", x, y, direction);
    fflush(stdout);
}

void API_clearWall(int x, int y, char direction) {
    printf("clearWall %d %d %c\n", x, y, direction);
    fflush(stdout);
}

void API_setColor(int x, int y, char color) {
    printf("setColor %d %d %c\n", x, y, color);
    fflush(stdout);
}

void API_clearColor(int x, int y) {
    printf("clearColor %d %d\n", x, y);
    fflush(stdout);
}

void API_clearAllColor(void) {
    printf("clearAllColor\n");
    fflush(stdout);
}

void API_setText(int x, int y, const char* str) {
    printf("setText %d %d %s\n", x, y, str ? str : "");
    fflush(stdout);
}

void API_clearText(int x, int y) {
    printf("clearText %d %d\n", x, y);
    fflush(stdout);
}

void API_clearAllText(void) {
    printf("clearAllText\n");
    fflush(stdout);
}

int API_wasReset(void) {
    char response[BUFFER_SIZE];
    getString("wasReset", response);
    return strcmp(response, "true") == 0;
}

void API_ackReset(void) {
    char response[BUFFER_SIZE];
    getString("ackReset", response);
    (void)response;
}
