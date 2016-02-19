#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <time.h>

#define fsz 5 //feature size

#define MAXSZ 891

#define numdata 500

#define min(a, b) ((a) <= (b) ? (a) : (b))
#define max(a, b) ((a) >= (b) ? (a) : (b))

float C = 1;
float error_cache[MAXSZ];
float alpha[MAXSZ];
float b;
float tol = 1e-3;
float eps = 1e-5;

float data[MAXSZ][fsz] = {};
float target[MAXSZ] = {};

float kernel(const float * a, const float * b) {
    int i;
    float r = 0;
    for (i = 0; i < fsz; ++i) {
        r += a[i] * b[i];
    }
    return (r + 1) * (r + 1);
}

int classify(float * x) {
    float r = 0;
    int i;
    for (i = 0; i < numdata; ++i) {
        if (alpha[i] > 0) {
            r += alpha[i] * target[i] * kernel(data[i], x);
        }
    }
    return r >= b ? 1 : -1;
}

#define getError(i) (error_cache[i])
//float getError(int ind) {
//    return error_cache[ind];
//}

int takestep(int i1, int i2) {
    if (i1 == i2) return 0;
    float alph1 = alpha[i1];
    float alph2 = alpha[i2];
    float y1 = target[i1];
    float y2 = target[i2];
    float bold = b;
    float s = y1 * y2;
    float gamma = alph1 + s * alph2;
    float L, H;
    if (s == -1) {
        L = max(0, alph2 - alph1);
        H = min(C, C + alph2 - alph1);
    } else {
        L = max(0, alph1 + alph2 - C);
        H = min(C, alph1 + alph2);
    }
    if (L == H) return 0;
    float k11 = kernel(data[i1], data[i1]);
    float k12 = kernel(data[i1], data[i2]);
    float k22 = kernel(data[i2], data[i2]);
    float eta = 2 * k12 - k11 - k22;
    float E1 = getError(i1);
    float E2 = getError(i2);
    float a2;
    if (eta < 0) {
        a2 = alph2 - y2 * (E1 - E2) / eta;
        if (a2 < L) a2 = L;
        if (a2 > H) a2 = H;
    } else {
        float v1, v2;
        v1 = getError(i1) + y1 + bold - y1 * alph1 * k11 - y2 * alph2 * k12; 
        v2 = getError(i2) + y2 + bold - y1 * alph1 * k12 - y2 * alph2 * k22; 
        float Lobj = L * (1 - s) 
            - 0.5 * k11 * (gamma - s * L) * (gamma - s * L)
            - 0.5 * k22 * L * L 
            - (gamma - s * L) * (s * k12 * L + y1 * v1)
            - y2 * L * v2;
        float Hobj = H * (1 - s) 
            - 0.5 * k11 * (gamma - s * H) * (gamma - s * H)
            - 0.5 * k22 * H * H 
            - (gamma - s * H) * (s * k12 * H + y1 * v1)
            - y2 * H * v2;
        if (Lobj > Hobj + eps) a2 = L;
        else if (Lobj < Hobj - eps) a2 = H;
        else a2 = alph2;
    }
    if (fabs(a2) < 1e-8) a2 = 0;
    else if (fabs(a2 - C) < 1e-8) a2 = C;
    if (fabs(a2 - alph2) < eps * (a2 + alph2 + eps)) return 0;
    float a1 = alph1 + s * (alph2 - a2);
    if (a1 < 0) a1 = 0;
    float b1 = bold + E1 + y1 * (a1 - alph1) * k11 + y2 * (a2 - alph2) * k12;
    float b2 = bold + E2 + y1 * (a1 - alph1) * k12 + y2 * (a2 - alph2) * k22;
    b = (b1 + b2) / 2;
    alpha[i1] = a1;
    alpha[i2] = a2;
    int i;
    float del1 = y1 * (a1 - alph1);
    float del2 = y2 * (a2 - alph2);
    for (i = 0; i < numdata; ++i) {
        float kr1 = kernel(data[i1], data[i]);
        float kr2 = kernel(data[i2], data[i]);
        error_cache[i] += del1 * kr1 + del2 * kr2 + bold - b;
    }
    return 1;
}

int ex_example(int i2) {
    float y2 = target[i2];
    float alph2 = alpha[i2];
    float E2 = getError(i2);
    float r2 = E2 * y2;
    int i;
    if ((r2 < -tol && alph2 < C) || (r2 > tol && alph2 > 0)) {
        int c = 0;
        for (i = 0; i < numdata; ++i) {
            c += alpha[i] > 0 && alpha[i] < C;
        }
        if (c > 1) {
            int i1 = -1;
            float err;
            for (i = 0; i < numdata; ++i) {
                if (i != i2) {
                    float e1 = fabs(E2 - getError(i));
                    if (i1 == -1 || e1 > err) {
                        i1 = i;
                        err = e1;
                    }
                }
            }
            if (takestep(i1, i2)) return 1;
        }
        for (i = 0; i < numdata; ++i) {
            if (alpha[i] > 0 && alpha[i] < C && takestep(i, i2))
                return 1;
        }
        for (i = 0; i < numdata; ++i) {
            if (takestep(i, i2)) return 1;
        }
    }
    return 0;
}

void main_routine() {
    b = 0;
    int i;
    for (i = 0; i < numdata; ++i) {
        alpha[i] = 0;
        error_cache[i] = -target[i];
    }
    int numChanged = 0, examineAll = 1;
    while (numChanged || examineAll) {
        numChanged = 0;
        if (examineAll) {
            for (i = 0; i < numdata; ++i) {
                numChanged += ex_example(i);
            }
        } else {
            for (i = 0; i < numdata; ++i) {
                if (alpha[i] > 0 && alpha[i] < C) {
                    numChanged += ex_example(i);
                }
            }
        }
        if (examineAll) examineAll = 0;
        else if (numChanged == 0) examineAll = 1;
    }
}

void load() {
    FILE * fp = fopen("out", "r");
    int i;
    int j;
    for (i = 0; i < MAXSZ; ++i) {
        for (j = 0; j < fsz; ++j) {
            fscanf(fp, "%f", data[i] + j);
        }
    }
    for (i = 0; i < MAXSZ; ++i) {
        fscanf(fp, "%f", target + i);
        printf("%f\n", target[i]);
    }
}

int main() {
    load();
    clock_t start = clock();
    main_routine();
    printf("Tot time = %.8f\n", (clock() - start) / (float)CLOCKS_PER_SEC);
    int i = 0;
    int r = 0;
    for (i = 0; i < numdata; ++i) {
        //printf("%d %f\n", classify(data[i]), target[i]);
        r += classify(data[i]) == target[i];
    }
    printf("accuracy = %f\n", r / (float)(numdata));
    return 0;
}
