#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <math.h>
#include <time.h>

#define min(a, b) ((a) <= (b) ? (a) : (b))
#define max(a, b) ((a) >= (b) ? (a) : (b))
//assumes at most 2000 training samples
float kernels[2000][2000];
typedef struct Smoinfo {
    float tol, eps; //constants
    float * error_cache, * alpha;
    float * W;
    float b;
    const float * data, * target;
    float C;
    int numdata, fsz;
} Smoinfo;

//only linear currently is supported now
float kernel(const float * a, const float * b, Smoinfo * info) {
    int i;
    float r = 0;
    for (i = 0; i < info->fsz; ++i) {
        r += a[i] * b[i];
    }
    return r; //linear
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

int update(int i1, int i2, Smoinfo * info) {
    if (i1 == i2) return 0;
    float alph1 = info->alpha[i1];
    float alph2 = info->alpha[i2];
    float y1 = info->target[i1];
    float y2 = info->target[i2];
    float bold = info->b;
    float L, H;
    if (y1 != y2) {
        L = max(0, alph2 - alph1);
        H = min(info->C, info->C + alph2 - alph1);
    } else {
        L = max(0, alph1 + alph2 - info->C);
        H = min(info->C, alph1 + alph2);
    }
    if (L == H) return 0;
    const float * d1 = &info->data[i1 * info->fsz];
    const float * d2 = &info->data[i2 * info->fsz];
    float k11 = kernels[i1][i1];
    float k12 = kernels[i1][i2];
    float k22 = kernels[i2][i2];
    float eta = 2 * k12 - k11 - k22;
    float a2;
    if (eta < 0) {
        a2 = y2 * (kernel(info->W, d2, info) - y2) - y2 * (kernel(info->W, d1, info) - y1);
        a2 = alph2 + a2 / eta;
        if (a2 < L) a2 = L;
        if (a2 > H) a2 = H;
    } else {
        assert(0);
    }
    if (fabs(a2) < 1e-8) a2 = 0;
    else if (fabs(a2 - info->C) < 1e-8) a2 = info->C;
    if (fabs(a2 - alph2) < info->eps) return 0;
    float a1 = alph1 + y1 * y2 * (alph2 - a2);
    if (a1 < 0) a1 = 0;
    int i, p;
    float da1 = a1 - alph1;
    float da2 = a2 - alph2;
    for (i = 0; i < info->fsz; ++i) {
        info->W[i] += da1 * y1 * d1[i] + da2 * y2 * d2[i];
    }
    float b1 = kernel(info->W, d1, info) - y1;
    float b2 = kernel(info->W, d2, info) - y2;
    info->b = (b1 + b2) / 2;
    info->alpha[i1] = a1;
    info->alpha[i2] = a2;
    return 1;
}

void main_routine(Smoinfo * info) {
    info->b = 0;
    int i;
    for (i = 0; i < info->numdata; ++i) {
        info->alpha[i] = 0;
    }
    for (i = 0; i < info->fsz; ++i) {
        info->W[i] = 0;
    }
    while (1) {
        int ch = 0, j;
        for (i = 0; i < info->numdata; ++i) {
            for (j = i + 1; j < info->numdata; ++j) {
                ch += update(i, j, info);
            }
        }
        if (ch == 0) break;
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
    for (i = p = 0; i < info->numdata; ++i, p += info->fsz) {
        printf("%f ", info->alpha[i]);
    }
    printf("\n");
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
    //precompute kernel matrix
    for (i = 0; i < num_data; ++i) {
        int j;
        for (j = i; j < num_data; ++j) {
            const float * p1 = &data[i * info.fsz];
            const float * p2 = &data[j * info.fsz];
            kernels[i][j] = kernels[j][i] = kernel(p1, p2, &info);
        }
    }
    info.alpha = alpha;
    info.error_cache = error_cache;
    info.tol = 1e-3;
    info.eps = 1e-5;
    float W[10000];
    info.W = W;
    info.C = 1;
    //main_routine(&info);
    routine2(&info);
    return info.b;
}

int main() {
    int num_data = 8;
    int num_features = 2;

    float data[] = { 
        0.3858, 0.4687,
        0.4871, 0.611, 
        0.9218, 0.4103,
        0.7382, 0.8936,
        0.1763, 0.0579,
        0.4057, 0.3529,
        0.9355, 0.8132,
        0.2146, 0.0099,
    };

    float target[8] = {1, -1, -1, -1, 1, 1, -1, 1};
    float alpha[8];
    float error_cache[8];
    int i = 0;
    for (i = 0; i < 8; ++i) error_cache[i] = 0;
    solve(data, target, alpha, error_cache, num_data, num_features);
    return 0;
}
