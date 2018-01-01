#include <stdio.h>
#include <math.h>
#include <string.h>

#define LEVELS 500
#define BITS_PER_VALUE 52

typedef double row[LEVELS/2+1];
row s[LEVELS];
row u[LEVELS];
row s1[LEVELS];

double alpha = 0.502;
double beta = 0.4;
double gamma1 = 0.0001;
int steps = 10000;

int rowSize(int i) { 
    return i == 0 ? 1 : ceil((i+1.)/2);
}

static double get(row *v,int i,int j) {
    if (i >= LEVELS)
        return beta;
    if (i<0)
        return v[1][0];
    if (i <= 1 && j != 0)
        j = 0;
    if (j < 0)
        return get(v,i,-j);
    int rs = rowSize(i);
    if (j >= rs) {
        if (i % 2)
            return get(v,i,rs-1-(j-rs));
        else
            return get(v,i,rs-2-(j-rs));
    }
    return v[i][j];
}

static void calculateU(void) {
    for(int i=0;i<LEVELS;i++)
        for(int j=0;j<rowSize(i);j++) {
            if (i==0) {
                u[i][j] = s[0][0]>=1 || s[1][0]>=1 ? 0. : s[i][j];
            }
            else if (j==0) {
                u[i][j] = s[i][j]>=1 || get(s,i,1)>=1 || get(s,i+1,0)>=1 || get(s,i+1,1)>=1 || get(s,i-1,0)>=1 ? 0. : s[i][j];
            }
            else {
                u[i][j] = s[i][j]>=1 || get(s,i,j-1)>=1 || get(s,i,j+1)>=1 || 
                          get(s,i+1,j)>=1 || get(s,i+1,j+1)>=1 || get(s,i-1,j)>=1 || get(s,i-1,j-1)>=1 
                                ? 0. : s[i][j];
            }
        }
}

static inline double uSum(int i, int j) {
    if (i==0)
        return 6.*u[1][0];
    if(j==0) 
        return 2*(get(u,i,1)+get(u,i+1,1))+get(u,i+1,0)+get(u,i-1,0);
    if(j<0)
        j=-j;
    return get(s,i,j-1) + get(s,i,j+1) + get(s,i+1,j) + get(s,i+1,j+1) + get(s,i-1,j) + get(s,i-1,j-1);
}

static void stepToS1(void) {
    for(int i=0;i<LEVELS;i++)
        for(int j=0;j<rowSize(i);j++) {
            s1[i][j] = (u[i][j]==0. ? s[i][j]+gamma1 : 1.-alpha/2.*u[i][j]) + alpha/12.*uSum(i,j);                        
        }
}

int main(int argc, char** argv) {
    if (argc > 1) {
        alpha = atof(argv[1]);
    }
    if (argc > 2) {
        beta = atof(argv[2]);
    }
    if (argc > 3) {
        beta = atof(argv[3]);
    }
    if (argc > 4) {
        steps = atof(argv[4]);
    }
    
    for (int i=0;i<LEVELS;i++)
        for(int j=0;j<rowSize(i);j++)
            s[i][j] = beta;
    s[0][0] = 1.;
    
    for (int step=0; step<steps; step++) {
        if(step%10==0)
            fprintf(stderr,"[%d]",step);
        
        calculateU();
        stepToS1();
        memcpy(s, s1, sizeof(s));
    }
    
    printf("<?xml version='1.0' ?>\n");
    printf("<xml xmlns='https://blockscad3d.com'>\n");
    printf("<version num='1.10.2'/>");
    for (int i=0;i<LEVELS;i++) {
        int rs = rowSize(i);
        for(int j=0;j<rs;j+=BITS_PER_VALUE) {
            long long v=0;
            for (int k=0;k<BITS_PER_VALUE;k++)
                if (s[i][j+k]>=1.) {
                    v += (double)((long long)1 << k);
                }
            if (v!=0) {
                printf("<block type='procedures_callreturn'><mutation name='draw'>\n");
                printf(" <arg name='i'/><arg name='j'/><arg name='v'/>\n");
                printf("</mutation>\n");
                printf("<value name='ARG0'><block type='math_number'><field name='NUM'>%d</field></block></value>\n", i);
                printf("<value name='ARG1'><block type='math_number'><field name='NUM'>%d</field></block></value>\n", j);
                printf("<value name='ARG2'><block type='math_number'><field name='NUM'>%lld</field></block></value>\n", v);
                printf("</block>");
            }
            
        }
    }
    printf("</xml>");
    
    return 0;
}

