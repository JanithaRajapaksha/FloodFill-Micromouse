CC ?= gcc
CFLAGS ?= -Wall -Wextra -Werror -pedantic -std=c99 -O2
LDFLAGS ?= $(CFLAGS)
INCLUDES = -Iinclude

SRCDIR = src
INCDIR = include
TESTDIR = tests
OBJDIR = obj
BINDIR = bin

COMMON_SRCS = $(SRCDIR)/maze_map.c \
              $(SRCDIR)/floodfill_core.c \
              $(SRCDIR)/sensor_interface.c \
              $(SRCDIR)/navigator.c \
              $(SRCDIR)/motor_controller.c \
              $(SRCDIR)/mazes.c

COMMON_OBJS = $(patsubst $(SRCDIR)/%.c, $(OBJDIR)/%.o, $(COMMON_SRCS))

MAIN_SRC = $(SRCDIR)/main.c
MAIN_OBJ = $(OBJDIR)/main.o
MAIN_BIN = $(BINDIR)/main

TEST_SRC = $(TESTDIR)/test_embedded.c
TEST_OBJ = $(OBJDIR)/test_embedded.o
TEST_BIN = $(BINDIR)/test_embedded

.PHONY: all clean test run asan

all: $(MAIN_BIN) $(TEST_BIN)

$(OBJDIR):
	mkdir -p $(OBJDIR)

$(BINDIR):
	mkdir -p $(BINDIR)

$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(TEST_OBJ): $(TEST_SRC) | $(OBJDIR)
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

$(MAIN_BIN): $(COMMON_OBJS) $(MAIN_OBJ) | $(BINDIR)
	$(CC) $(LDFLAGS) $(COMMON_OBJS) $(MAIN_OBJ) -o $@

$(TEST_BIN): $(COMMON_OBJS) $(TEST_OBJ) | $(BINDIR)
	$(CC) $(LDFLAGS) $(COMMON_OBJS) $(TEST_OBJ) -o $@

test: $(TEST_BIN)
	$(TEST_BIN)

run: $(MAIN_BIN)
	$(MAIN_BIN)

# AddressSanitizer and UndefinedBehaviorSanitizer build for memory safety verification
asan: CFLAGS += -fsanitize=address,undefined -g
asan: clean all
	$(TEST_BIN)

clean:
	rm -rf $(OBJDIR) $(BINDIR)
