#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <time.h>

#define min(a, b) ((a) <= (b) ? (a) : (b))
#define max(a, b) ((a) >= (b) ? (a) : (b))

typedef struct Smoinfo {
    float tol, eps; //constants
    float * error_cache, * alpha;
    float b;
    const float * data, * target;
    float C;
    int numdata, fsz;
} Smoinfo;

float kernel(const float * a, const float * b, Smoinfo * info) {
    int i;
    float r = 0;
    for (i = 0; i < info->fsz; ++i) {
        r += a[i] * b[i];
    }
    return (r + 1) * (r + 1);
}

int classify(const float * x, Smoinfo * info) {
    float r = 0;
    int i, p;
    for (i = p = 0; i < info->numdata; ++i, p += info->fsz) {
        if (info->alpha[i] > 0) {
            r += info->alpha[i] * info->target[i] * kernel(&info->data[p], x, info);
        }
    }
    return r >= info->b ? 1 : -1;
}

float func(const float * x, Smoinfo * info) {
    float r = 0;
    int i, p;
    for (i = p = 0; i < info->numdata; ++i, p += info->fsz) {
        if (info->alpha[i] > 0) {
            r += info->alpha[i] * info->target[i] * kernel(&info->data[p], x, info);
        }
    }
    return r - info->b;
}

float getError(int i, Smoinfo * info) {
    return (info->alpha[i] > 0 && info->alpha[i] < info->C) ? info->error_cache[i] : func(&info->data[(i) * info->fsz], info) - info->target[i];
}

int takestep(int i1, int i2, Smoinfo * info) {
    if (i1 == i2) return 0;
    float alph1 = info->alpha[i1];
    float alph2 = info->alpha[i2];
    float y1 = info->target[i1];
    float y2 = info->target[i2];
    float bold = info->b;
    float s = y1 * y2;
    float gamma = alph1 + s * alph2;
    float L, H;
    if (s == -1) {
        L = max(0, alph2 - alph1);
        H = min(info->C, info->C + alph2 - alph1);
    } else {
        L = max(0, alph1 + alph2 - info->C);
        H = min(info->C, alph1 + alph2);
    }
    if (L == H) return 0;
    const float * d1 = &info->data[i1 * info->fsz];
    const float * d2 = &info->data[i2 * info->fsz];
    float k11 = kernel(d1, d1, info);
    float k12 = kernel(d1, d2, info);
    float k22 = kernel(d2, d2, info);
    float eta = 2 * k12 - k11 - k22;
    float E1 = getError(i1, info);
    float E2 = getError(i2, info);
    float a2;
    if (eta < 0) {
        a2 = alph2 - y2 * (E1 - E2) / eta;
        if (a2 < L) a2 = L;
        if (a2 > H) a2 = H;
    } else {
        float c2 = y2 * (E1 - E2);
        float Lobj = c2 * L;
        float Hobj = c2 * H;
        if (Lobj > Hobj + info->eps) a2 = L;
        else if (Lobj < Hobj - info->eps) a2 = H;
        else a2 = alph2;
    }
    if (fabs(a2) < 1e-8) a2 = 0;
    else if (fabs(a2 - info->C) < 1e-8) a2 = info->C;
    if (fabs(a2 - alph2) < info->eps * (a2 + alph2 + info->eps)) return 0;
    float a1 = alph1 + s * (alph2 - a2);
    if (a1 < 0) a1 = 0;
    float b1 = bold + E1 + y1 * (a1 - alph1) * k11 + y2 * (a2 - alph2) * k12;
    float b2 = bold + E2 + y1 * (a1 - alph1) * k12 + y2 * (a2 - alph2) * k22;
    info->b = (b1 + b2) / 2;
    int i, p;
    float del1 = y1 * (a1 - alph1);
    float del2 = y2 * (a2 - alph2);
    info->alpha[i1] = a1;
    info->alpha[i2] = a2;
    for (i = 0, p = 0; i < info->numdata; ++i, p += info->fsz) {
        if (info->alpha[i] > 0 && info->alpha[i] < info->C) {
            float kr1 = kernel(d1, &info->data[p], info);
            float kr2 = kernel(d2, &info->data[p], info);
            info->error_cache[i] += del1 * kr1 + del2 * kr2 + bold - info->b;
        }
    }
    //a1 was in bounds previously
    //but not now, so need to get new error value
    if (alph1 == 0 || alph1 == info->C) { 
        if (a1 > 0 && a1 < info->C) {
            info->error_cache[i1] = func(d1, info) - info->target[i1];
        }
    }
    if (alph2 == 0 || alph2 == info->C) {
        if (a2 > 0 && a2 < info->C) {
            info->error_cache[i2] = func(d2, info) - info->target[i2];
        }
    }
    return 1;
}

int ex_example(int i2, Smoinfo * info) {
    float y2 = info->target[i2];
    float alph2 = info->alpha[i2];
    float E2 = getError(i2, info);
    float r2 = E2 * y2;
    int i;
    if ((r2 < -info->tol && alph2 < info->C) || (r2 > info->tol && alph2 > 0)) {
        int i1 = -1;
        float err;
        for (i = 0; i < info->numdata; ++i) {
            if (i != i2 && info->alpha[i] > 0 && info->alpha[i] < info->C) {
                float e1 = fabs(E2 - getError(i, info));
                if (i1 == -1 || e1 > err) {
                    i1 = i;
                    err = e1;
                }
            }
        }
        if (i1 != -1 && takestep(i1, i2, info)) return 1;
        for (i = 0; i < info->numdata; ++i) {
            if (info->alpha[i] > 0 && info->alpha[i] < info->C && takestep(i, i2, info))
                return 1;
        }
        for (i = 0; i < info->numdata; ++i) {
            if (takestep(i, i2, info)) return 1;
        }
    }
    return 0;
}

void main_routine(Smoinfo * info) {
    info->b = 0;
    int i;
    for (i = 0; i < info->numdata; ++i) {
        info->alpha[i] = 0;
    }
    int numChanged = 0, examineAll = 1;
    while (numChanged || examineAll) {
        numChanged = 0;
        if (examineAll) {
            for (i = 0; i < info->numdata; ++i) {
                numChanged += ex_example(i, info);
            }
        } else {
            for (i = 0; i < info->numdata; ++i) {
                if (info->alpha[i] > 0 && info->alpha[i] < info->C) {
                    numChanged += ex_example(i, info);
                }
            }
        }
        if (examineAll) examineAll = 0;
        else if (numChanged == 0) examineAll = 1;
    }
}

int routine2(Smoinfo * info) {
    clock_t start = clock();
    main_routine(info);
    printf("Tot time = %.8f\n", (clock() - start) / (float)CLOCKS_PER_SEC);
    int i = 0, p;
    int r = 0;
    for (i = p = 0; i < info->numdata; ++i, p += info->fsz) {
        r += classify(info->data + p, info) == info->target[i];
    }
    printf("accuracy = %f\n", r / (float)(info->numdata));
    return 0;
}

//returns bias
//main interface used by the bsvm.py module
//
float solve(const float * data, const float * target, float * alpha, float * error_cache, int num_data, int num_features) {
    int i;
    Smoinfo info;
    info.numdata = num_data;
    info.fsz = num_features;
    info.data = data;
    info.target = target;
    info.alpha = alpha;
    info.error_cache = error_cache;
    info.tol = 1e-3;
    info.eps = 1e-5;
    info.C = 1;
    main_routine(&info);
    return info.b;
}
