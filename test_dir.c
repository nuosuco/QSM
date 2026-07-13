// Test script to check get_directory_entries at depth
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

int main() {
    const char *paths[] = {
        "./QEntL",
        "./QEntL/docs",
        "./QEntL/Models",
        "./QEntL/Models/QSM",
        "./QEntL/Models/QSM/docs",
        NULL
    };
    for (int pi = 0; paths[pi]; pi++) {
        printf("--- %s ---\n", paths[pi]);
        DIR *d = opendir(paths[pi]);
        if (!d) { printf("FAILED\n"); continue; }
        struct dirent *de;
        int count = 0;
        while ((de = readdir(d)) != NULL) {
            if (strcmp(de->d_name, ".") == 0 || strcmp(de->d_name, "..") == 0) continue;
            count++;
        }
        closedir(d);
        printf("  entries=%d\n", count);
    }
    return 0;
}