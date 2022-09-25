#include <stdio.h>
#include <stdlib.h>
#include "rsa.h"

bytes to_bytes(const unsigned long long n) {
    st size = 1;
    unsigned long long tmp = n;
    while (tmp /= 256)
        size++;
    byte *data = malloc(size * sizeof(byte));
    tmp = n;
    for (st i = 0; i < size; i++) {
        data[i] = tmp % 256;
        tmp /= 256;
    }
    return (bytes){data, size};
}

unsigned long long to_ull(const bytes a) {
    unsigned long long n = 0;
    for (st i = 0; i < a.size; i++)
        n += a.data[i] * (1 << (8 * i));
    return n;
}

void print_bytes(bytes b) {
    for (st i = b.size - 1; i < b.size; i--)
        printf("%02x", b.data[i]);
}

bytes add(const bytes a, const bytes b) {
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

bytes mul(const bytes a, const bytes b) {
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

bytes half(const bytes a) {
    st size = a.size;
    byte data[size];
    int carry = 0;
    for (st i = size - 1; i < size; i--) {
        int sum = a.data[i] + carry * 256;
        data[i] = sum / 2;
        carry = sum % 2;
    }
    while (size > 1 && data[size - 1] == 0) size--;
    return (bytes){data, size};
}

bytes mod(const bytes a, const bytes b) {
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
    data = realloc(data, size * sizeof(byte));
    return (bytes){data, size};
}

bytes pow_mod(const bytes a, const bytes b, const bytes c) {
    // printf("%llu ^ %llu mod %llu\n", to_ull(a), to_ull(b), to_ull(c));
    if (b.size == 1 && b.data[0] == 0) return to_bytes(1);
    if (b.data[0] % 2) return mod(mul(a, pow_mod(mod(mul(a, a), c), half(b), c)), c);
    return mod(pow_mod(mul(a, a), half(b), c), c);
}

int main() {
    bytes a = to_bytes(2);
    bytes b = to_bytes(3);
    bytes c = to_bytes(5);
    print_bytes(pow_mod(a, b, c));
    printf("\n");
}