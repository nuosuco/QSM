/**
 * QEntL闂佹彃绻愰悺娆撴偐閼哥鍋撴担鍝ユ澖闁绘粎澧楅弸鍐╃?- 缂佺姭鍋撻柛鏍ㄧ墱婢? * 
 * @闁哄倸娲ｅ▎? quantum_state.c
 * @闁硅绻楅崼? 閻庡湱鍋熼獮鍥煂韫囨挾鎽嶉柟顑胯兌濞堟垿宕洪悜妯绘嫳缂備焦鎸婚悗顖炲椽鐏炵偓鎯欏ù锝嗙矊閸ら亶寮? * @闁绘鐗婂﹢? 1.0
 */

#include "quantum_state.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <complex.h>

/* -------------------- 闂佹彃绻愰悺娆撴偐閼哥鍋撴担绋挎瘣闁轰焦婢橀悿鍕偝?-------------------- */

QState* quantum_state_create(const char* name) {
    if (!name) {
        return NULL;
    }
    
    QState* state = (QState*)malloc(sizeof(QState));
    if (!state) {
        return NULL;
    }
    
    /* 闁告帗绻傞～鎰板礌閺嵮呭敤闁哄牜鍓欓悺褍鈻?*/
    state->name = strdup(name);
    if (!state->name) {
        free(state);
        return NULL;
    }
    
    state->type = QSTATE_BASIC;
    state->state_data = NULL;
    state->quantum_gene = NULL;
    state->entanglements = NULL;
    state->entanglement_count = 0;
    state->properties = NULL;
    state->property_values = NULL;
    state->property_count = 0;
    
    /* 濮掓稒顭堥濠氬礆濠靛棭娼楅柛鏍ㄧ墧鐠愮劜0闁村嫧鏅濇慨鎼佸箑?*/
    state->alpha = 1.0 + 0.0 * I;
    state->beta = 0.0 + 0.0 * I;
    
    return state;
}

void quantum_state_destroy(QState* state) {
    if (!state) {
        return;
    }
    
    /* 闂佹彃锕ラ弬渚€宕ュ鍥?*/
    if (state->name) {
        free(state->name);
    }
    
    /* 闂佹彃锕ラ弬渚€鎮╅懜纰樺亾娴ｈ娈堕柟?*/
    if (state->state_data) {
        free(state->state_data);
    }
    
    /* 闂佹彃锕ラ弬浣虹棯閻樼數鐐婇柡浣瑰缁?*/
    if (state->entanglements) {
        free(state->entanglements);
    }
    
    /* 闂佹彃锕ラ弬浣轰沪閻愮补鍋撹閺嗙喓绱?*/
    if (state->properties) {
        for (size_t i = 0; i < state->property_count; i++) {
            if (state->properties[i]) {
                free(state->properties[i]);
            }
        }
        free(state->properties);
    }
    
    /* 闂佹彃锕ラ弬浣轰沪閻愮补鍋撹閳ь剙鍚嬮弳鐔虹磼?*/
    if (state->property_values) {
        for (size_t i = 0; i < state->property_count; i++) {
            if (state->property_values[i]) {
                free(state->property_values[i]);
            }
        }
        free(state->property_values);
    }
    
    /* 闂佹彃锕ラ弬渚€鎮╅懜纰樺亾娴ｈ櫣娉㈤柡瀣缂?*/
    free(state);
}

int quantum_state_set_property(QState* state, const char* name, const char* value) {
    if (!state || !name || !value) {
        return 0;
    }
    
    /* 闁哄被鍎叉竟姗€寮伴姘剨鐎瑰憡褰冮悺銊╁捶閵娧勭ゲ闁告艾鑻惈姗€骞€?*/
    for (size_t i = 0; i < state->property_count; i++) {
        if (strcmp(state->properties[i], name) == 0) {
            /* 闁哄洤鐡ㄩ弻濠勪沪閻愮补鍋撹閳?*/
            free(state->property_values[i]);
            state->property_values[i] = strdup(value);
            return 1;
        }
    }
    
    /* 闁圭鏅涢惈宥囦沪閻愮补鍋撹閺嗙喓绱?*/
    char** new_props = (char**)realloc(state->properties, 
                                       (state->property_count + 1) * sizeof(char*));
    if (!new_props) {
        return 0;
    }
    state->properties = new_props;
    
    /* 闁圭鏅涢惈宥囦沪閻愮补鍋撹閳ь剙鍚嬮弳鐔虹磼?*/
    char** new_values = (char**)realloc(state->property_values, 
                                        (state->property_count + 1) * sizeof(char*));
    if (!new_values) {
        return 0;
    }
    state->property_values = new_values;
    
    /* 婵烇綀顕ф慨鐐哄棘閺夎法娼ｉ柟?*/
    state->properties[state->property_count] = strdup(name);
    state->property_values[state->property_count] = strdup(value);
    state->property_count++;
    
    return 1;
}

const char* quantum_state_get_property(QState* state, const char* name) {
    if (!state || !name) {
        return NULL;
    }
    
    /* 闁哄被鍎叉竟妯间沪閻愮补鍋?*/
    for (size_t i = 0; i < state->property_count; i++) {
        if (strcmp(state->properties[i], name) == 0) {
            return state->property_values[i];
        }
    }
    
    return NULL;
}

int quantum_state_apply_gene(QState* state, QGene* gene) {
    if (!state || !gene) {
        return 0;
    }
    
    /* 閻犱礁澧介悿鍡涘春閸濆嫭绀堥柡宥呮穿椤?*/
    state->quantum_gene = gene;
    
    /* 閻犱礁澧介悿鍡涙偐閼哥鍋撴担鍝ユ剑闁?*/
    quantum_state_set_property(state, "gene_applied", "true");
    
    return 1;
}

int quantum_state_add_entanglement(QState* state, QEntanglement* entanglement) {
    if (!state || !entanglement) {
        return 0;
    }
    
    /* 闁圭鏅涢惈宥囩棯閻樼數鐐婇柡浣瑰缁?*/
    QEntanglement** new_entanglements = (QEntanglement**)realloc(state->entanglements, 
                                                              (state->entanglement_count + 1) * sizeof(QEntanglement*));
    if (!new_entanglements) {
        return 0;
    }
    
    state->entanglements = new_entanglements;
    state->entanglements[state->entanglement_count] = entanglement;
    state->entanglement_count++;
    
    return 1;
}

QState* quantum_state_clone(QState* state) {
    if (!state) {
        return NULL;
    }
    
    /* 闁告帗绋戠紓鎾诲棘閹殿喖笑闁?*/
    QState* clone = quantum_state_create(state->name);
    if (!clone) {
        return NULL;
    }
    
    /* 濠㈣泛绉撮崺妤呭春閻戞ɑ鎷遍悘鐐靛仦閳?*/
    clone->type = state->type;
    clone->alpha = state->alpha;
    clone->beta = state->beta;
    
    /* 濠㈣泛绉撮崺妤冧沪閻愮补鍋?*/
    for (size_t i = 0; i < state->property_count; i++) {
        quantum_state_set_property(clone, state->properties[i], state->property_values[i]);
    }
    
    return clone;
}

QState* quantum_state_measure(QState* state) {
    if (!state) {
        return NULL;
    }
    
    /* 闁告帗绋戠紓鎾诲棘閹殿喗鐣辩€圭寮剁粊鎾煂韫囨洖笑闁?*/
    QState* measured = quantum_state_clone(state);
    if (!measured) {
        return NULL;
    }
    
    /* 閻犱礁澧介悿鍡樼▔閸濆嫬鍤掓繛鏉戭儔閸ｈ櫣鐚剧拠鑼偓?*/
    measured->type = QSTATE_MEASURED;
    
    /* 閺夆晜绋栭、鎴濐潡閸屾粌鑺抽悹渚婄磿閻?*/
    double prob_0 = creal(state->alpha) * creal(state->alpha) + cimag(state->alpha) * cimag(state->alpha);
    double prob_1 = creal(state->beta) * creal(state->beta) + cimag(state->beta) * cimag(state->beta);
    
    /* 閻犱礁澧介悿鍡椕圭€ｎ喖娅ら悘鐐靛仦閳?*/
    quantum_state_set_property(measured, "measured", "true");
    
    /* 闁哄秷顫夊畵浣割潡閸屾粌鑺崇痪顓у枛閻ｆ儳霉鐎ｎ喖娅ょ紓浣规尰閻?*/
    if (prob_0 >= 0.5) {
        /* 婵炴潙顑夐崳铏圭磼閹惧浜☉鎾剁毟0闁?*/
        measured->alpha = 1.0 + 0.0 * I;
        measured->beta = 0.0 + 0.0 * I;
        quantum_state_set_property(measured, "result", "0");
            } else {
        /* 婵炴潙顑夐崳铏圭磼閹惧浜☉鎾剁毟1闁?*/
        measured->alpha = 0.0 + 0.0 * I;
        measured->beta = 1.0 + 0.0 * I;
        quantum_state_set_property(measured, "result", "1");
    }
    
    return measured;
}

void quantum_state_print(QState* state) {
    if (!state) {
        printf("缂佸本妞介崳铏光偓娑欏姉婵悂骞€娑旀");
        return;
    }
    
    printf("闂佹彃绻愰悺娆撴偐閼哥鍋? %s\n", state->name);
    printf("缂侇偉顕ч悗? %d\n", state->type);
    printf("闁瑰壊鍨扮粻? alpha=%.2f%+.2fi, beta=%.2f%+.2fi\n", 
           creal(state->alpha), cimag(state->alpha),
           creal(state->beta), cimag(state->beta));
    
        printf("閻忕偟鍋為埀?\n");
        for (size_t i = 0; i < state->property_count; i++) {
            printf("  %s: %s\n", state->properties[i], state->property_values[i]);
        }
    }
    
MeasurementResult measure_qubit(QState* qubit) {
    MeasurementResult result;
    double prob_0 = creal(qubit->alpha) * creal(qubit->alpha) + cimag(qubit->alpha) * cimag(qubit->alpha);
    
    /* 缂佺姭鍋撻柛鏍ㄧ墬缁佹挳鏌岃箛銉х闁诡剛绮Σ鍛婃交閺傛寧绀€闁哄牃鍋撻柛娆樺灥閸忔﹢鎯冮崟顓犳尝闁?*/
    if (prob_0 >= 0.5) {
        result.result = 0;
        result.probability = prob_0;
        
        /* 閻忓繐妫涙慨鎼佸箑娴ｅ憡缍岀紓鍌楁櫃鐠愮劜0闁?*/
        qubit->alpha = 1.0 + 0.0 * I;
        qubit->beta = 0.0 + 0.0 * I;
    } else {
        result.result = 1;
        result.probability = 1.0 - prob_0;
        
        /* 閻忓繐妫涙慨鎼佸箑娴ｅ憡缍岀紓鍌楁櫃鐠愮劜1闁?*/
        qubit->alpha = 0.0 + 0.0 * I;
        qubit->beta = 1.0 + 0.0 * I;
    }
    
    return result;
} 
