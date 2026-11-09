#ifndef API_H
#define API_H

#ifdef __cplusplus
extern "C" {
#endif

int API_mazeWidth(void);
int API_mazeHeight(void);

int API_wallFront(void);
int API_wallRight(void);
int API_wallLeft(void);

int API_moveForward(void); // Returns 0 if crash, else returns 1
void API_turnRight(void);
void API_turnLeft(void);

void API_setWall(int x, int y, char direction);
void API_clearWall(int x, int y, char direction);

void API_setColor(int x, int y, char color);
void API_clearColor(int x, int y);
void API_clearAllColor(void);

void API_setText(int x, int y, const char* str);
void API_clearText(int x, int y);
void API_clearAllText(void);

int API_wasReset(void);
void API_ackReset(void);

#ifdef __cplusplus
}
#endif

#endif /* API_H */
