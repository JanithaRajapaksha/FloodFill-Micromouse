CC ?= gcc
CFLAGS ?= -static -Wall -Wextra -O2 -std=c99 -I.
TARGET = mouse.exe

SRCS = API.c maze_map.c floodfill_core.c navigator.c main.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET) mouse
