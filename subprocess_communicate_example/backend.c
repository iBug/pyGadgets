// File: kernel.c
// Author: iBug

#include <stdio.h>

int main() {
    int a, b, s;
    char op;
    while(1) {
        scanf(" %d %d", &a, &b);
        printf("%d\n", a + b);
        fflush(stdout);
    }
    return 0;
}
