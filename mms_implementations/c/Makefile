CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2 -std=c99 -I.
LDFLAGS ?= -Wl,--dynamicbase -Wl,--high-entropy-va -Wl,--nxcompat
TARGET = mouse.exe

SRCS = API.c maze_map.c floodfill_core.c navigator.c main.c mazes.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) mouse
