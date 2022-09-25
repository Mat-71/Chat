#include <stdio.h>
#include <stdlib.h>
#include "rsa.h"

bytes to_bytes(long long n) {
    st size = 1;
    long long tmp = n;
    while (tmp /= 256)
        size++;
    byte *data = malloc(size * sizeof(byte));
    for (st i = 0; i < size; i++) {
        data[i] = n % 256;
        n /= 256;
    }
    return (bytes){data, size};
}

int to_int(bytes a) {
    int n = 0;
    for (st i = 0; i < a.size; i++)
        n += a.data[i] * (1 << (8 * i));
    return n;
}

void print_bytes(bytes b) {
    for (st i = b.size - 1; i < b.size; i--)
        printf("%02x", b.data[i]);
}

bytes add(bytes a, bytes b) {
    st size = a.size > b.size ? a.size : b.size;
    byte data[size];
    int carry = 0;
    for (st i = 0; i < size; i++) {
        int sum = carry;
        if (i < a.size) sum += a.data[i];
        if (i < b.size) sum += b.data[i];
        data[i] = sum % 256;
        carry = sum / 256;
    }
    if (carry) {
        data[size] = carry;
        size++;
    }
    return (bytes){data, size};
}

bytes mul(bytes a, bytes b) {
    st size = a.size + b.size;
    byte data[size];
    for (st i = 0; i < size; i++)
        data[i] = 0;
    for (st i = 0; i < a.size; i++) {
        for (st j = 0; j < b.size; j++) {
            int sum = data[i + j] + a.data[i] * b.data[j];
            data[i + j] = sum % 256;
            data[i + j + 1] += sum / 256;
        }
    }
    while (size > 1 && data[size - 1] == 0) size--;
    return (bytes){data, size};
}

bytes mod(bytes a, bytes b) {
    st size = a.size;
    byte *data = malloc(size * sizeof(byte));
    for (st i = 0; i < size; i++)
        data[i] = a.data[i];
    int div, diff, carry;
    while (size >= b.size && (div = data[size - 1] / b.data[b.size - 1])) {
        if (div == 1) { // checks if data > b
            for (st i = 0; i < b.size; i++) {
                if (data[size - b.size + i] > b.data[i]) break;
                if (data[size - b.size + i] < b.data[i]) {
                    div = 0;
                    break;
                }
            }
        }
        if (!div) break;
        carry = 0;
        for (st i = 0; i < b.size; i++) {
            diff = data[size - b.size + i] - div * b.data[i] + carry;
            if (diff < 0) {
                if (diff % 256) {
                    carry = diff / 256 - 1;
                    diff = diff % 256 + 256;
                } else {
                    carry = diff / 256;
                    diff = 0;
                }
            }
            else carry = 0;
            data[size - b.size + i] = diff;
        }
        while (size > 1 && data[size - 1] == 0) size--;
    }
    return (bytes){data, size};
}

int main() {
    for (int a = 0; a < 100; a++) {
        for (int b = 1; b < 100; b++) {
            bytes A = to_bytes(a);
            bytes B = to_bytes(b);
            bytes C = mod(A, B);
            if (to_int(C) != a % b) {
                printf("a = %d, b = %d\n", a, b);
                print_bytes(A);
                printf(" %% ");
                print_bytes(B);
                printf(" = ");
                print_bytes(C);
                printf(" != %d\n", a % b);
                return 1;
            }
        }
    }
    return 0;
}