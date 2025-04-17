/**
 * QEntL闂佹彃绻愰悺娆撳春閸濆嫭绀堥悗鍦仧楠炲洭寮崶锔筋偨 - 缂佺姭鍋撻柛鏍ㄧ墱婢?
 * 
 * @闁哄倸娲ｅ▎? quantum_gene.c
 * @闁硅绻楅崼? 閻庡湱鍋熼獮鍥煂韫囨挾鎽嶉柛鈺佹惈濞叉粓鎯冮崟顐ゅ敤闁哄牜鍓涚划銊╁几閸曨偅瀚查柟鍨С缂嶆棃宕欓懞銉︽
 * @闁绘鐗婂﹢? 1.0
 */

#include "quantum_gene.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* -------------------- 闂佹彃绻愰悺娆撳春閸濆嫭绀堥柛鎴ｅГ閺嗙喓鈧湱鍋熼獮?-------------------- */

QGene* quantum_gene_create(const char* id, QGeneType type) {
    if (!id) {
        return NULL;
    }
    
    QGene* gene = (QGene*)malloc(sizeof(QGene));
    if (!gene) {
        return NULL;
    }
    
    /* 闁告帗绻傞～鎰板礌閺嵮呭敤闁哄牜鍓欓悺褍鈻?*/
    gene->id = strdup(id);
    if (!gene->id) {
        free(gene);
        return NULL;
    }
    
    gene->type = type;
    gene->properties = NULL;
    gene->property_count = 0;
    
    /* 闁告帗绻傞～鎰板礌閺嶎兙鈧啯娼忛幆褍妫橀柡?*/
    gene->expression.is_active = 0;
    gene->expression.strength = 0.0;
    gene->expression.stability = 0.0;
    gene->expression.mutation_rate = 0.01;
    
    return gene;
}

void quantum_gene_destroy(QGene* gene) {
    if (!gene) {
        return;
    }
    
    /* 闂佹彃锕ラ弬涓 */
    if (gene->id) {
        free(gene->id);
    }
    
    /* 闂佹彃锕ラ弬浣轰沪閻愮补鍋?*/
    if (gene->properties) {
        for (size_t i = 0; i < gene->property_count; i++) {
            if (gene->properties[i].name) {
                free(gene->properties[i].name);
            }
            if (gene->properties[i].value) {
                free(gene->properties[i].value);
            }
        }
        free(gene->properties);
    }
    
    /* 闂佹彃锕ラ弬渚€宕洪崫鍕缂備焦鎸婚悗顖涙媴?*/
    free(gene);
}

int quantum_gene_add_property(QGene* gene, const char* name, const char* value) {
    if (!gene || !name || !value) {
        return 0;
    }
    
    /* 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敃鈧崙锛勨偓娑櫭﹢顏嗘嫚閵夈儳娼ｉ柟?*/
    for (size_t i = 0; i < gene->property_count; i++) {
        if (strcmp(gene->properties[i].name, name) == 0) {
            /* 闁哄洤鐡ㄩ弻濠勪沪閻愮补鍋撹閳?*/
            free(gene->properties[i].value);
            gene->properties[i].value = strdup(value);
        return 1;
        }
    }
    
    /* 闁圭鏅涢惈宥囦沪閻愮补鍋撹閺嗙喓绱?*/
    QGeneProperty* new_props = (QGeneProperty*)realloc(gene->properties, 
                                                    (gene->property_count + 1) * sizeof(QGeneProperty));
    if (!new_props) {
        return 0;
    }
    
    gene->properties = new_props;
    
    /* 婵烇綀顕ф慨鐐哄棘閺夎法娼ｉ柟?*/
    gene->properties[gene->property_count].name = strdup(name);
    gene->properties[gene->property_count].value = strdup(value);
    gene->property_count++;
    
    return 1;
}

const char* quantum_gene_get_property(QGene* gene, const char* name) {
    if (!gene || !name) {
        return NULL;
    }
    
    /* 闁哄被鍎叉竟妯间沪閻愮补鍋?*/
    for (size_t i = 0; i < gene->property_count; i++) {
        if (strcmp(gene->properties[i].name, name) == 0) {
            return gene->properties[i].value;
        }
    }
    
    return NULL;
}

int quantum_gene_activate(QGene* gene, double strength) {
    if (!gene || strength < 0.0 || strength > 1.0) {
        return 0;
    }
    
    gene->expression.is_active = 1;
    gene->expression.strength = strength;
    
    return 1;
}

int quantum_gene_deactivate(QGene* gene) {
    if (!gene) {
        return 0;
    }
    
    gene->expression.is_active = 0;
    gene->expression.strength = 0.0;
    
    return 1;
}

QGene* quantum_gene_clone(QGene* gene) {
    if (!gene) {
        return NULL;
    }
    
    /* 闁告帗绋戠紓鎾诲棘閺夎法鍞ㄩ柛?*/
    QGene* clone = quantum_gene_create(gene->id, gene->type);
    if (!clone) {
        return NULL;
    }
    
    /* 濠㈣泛绉撮崺妤冩偘閵娿劍褰ч柛娆忓€归弳?*/
    clone->expression = gene->expression;
    
    /* 濠㈣泛绉撮崺妤冧沪閻愮补鍋?*/
    for (size_t i = 0; i < gene->property_count; i++) {
        quantum_gene_add_property(clone, gene->properties[i].name, gene->properties[i].value);
    }
    
    return clone;
}

int quantum_gene_mutate(QGene* gene) {
    if (!gene) {
        return 0;
    }
    
    /* 濞寸姴鎳庡﹢顏堝春閸濆嫭绀堟繛鍙夋缁岊剟寮幆鎵冲亾閸愵厽顎氱紒鎰瑜?*/
    if (!gene->expression.is_active) {
        return 0;
    }
    
    /* 闁哄秷顫夊畵浣虹玻娴ｇ缍侀柣婊冩搐閸犲懐鈧纰嶅Σ鎼佸触閿斿墽宕愰柛?*/
    double rand_val = (double)rand() / RAND_MAX;
    if (rand_val > gene->expression.mutation_rate) {
        return 0;  /* 濞戞挸绉堕悰濠囧矗?*/
    }
    
    /* 闁圭瑳鍡╂斀缂佹劒绀佽ぐ澶愭晬濮橆厽鏆柛娆愵焾閵嗗啯娼忛幆褍绻侀幖?*/
    double mutation_factor = 0.8 + ((double)rand() / RAND_MAX) * 0.4;  /* 0.8-1.2闁汇劌瀚板▓銏ゅ嫉閸濆嫭绀堥悗?*/
    gene->expression.strength *= mutation_factor;
    
    /* 缁绢収鍠曠换姘嚕閸濆嫬顔婇柛锔哄妽濠€渚€寮崼锝呯槺闁搞儲娼欓崬?*/
    if (gene->expression.strength > 1.0) {
        gene->expression.strength = 1.0;
    }
    
    /* 缂佹劒绀佽ぐ澶愬触鎼达姬鏃傗偓瑙勭閳ь儸鍛鐎甸偊鍣ｅ閿嬫媴?*/
    gene->expression.stability *= 0.95;
    
    return 1;
}

void quantum_gene_print(QGene* gene) {
    if (!gene) {
        printf("缂佸本妞介崳铏光偓娑欏姇閻斺偓闁搞儳鍤﹏");
        return;
    }
    
    printf("闂佹彃绻愰悺娆撳春閸濆嫭绀? %s\n", gene->id);
    printf("缂侇偉顕ч悗? %d\n", gene->type);
    printf("閻炴稏鍔忛幓顏堟偐閼哥鍋? %s\n", gene->expression.is_active ? "婵炲弶妲掔粚? : "闂傚牏鍋炲璺ㄦ崉?);
    printf("閻炴稏鍔忛幓顏勵嚕閸濆嫬顔? %.2f\n", gene->expression.strength);
    printf("缂佸鍟块悾楣冨箑? %.2f\n", gene->expression.stability);
    printf("缂佹劒绀佽ぐ澶愭偝? %.3f\n", gene->expression.mutation_rate);
    
    printf("閻忕偟鍋為埀?\n");
    for (size_t i = 0; i < gene->property_count; i++) {
        printf("  %s: %s\n", gene->properties[i].name, gene->properties[i].value);
    }
}

QGeneBank* quantum_gene_bank_create() {
    QGeneBank* bank = (QGeneBank*)malloc(sizeof(QGeneBank));
    if (!bank) {
        return NULL;
    }
    
    bank->genes = NULL;
    bank->gene_count = 0;
    
    return bank;
}

void quantum_gene_bank_destroy(QGeneBank* bank) {
    if (!bank) {
        return;
    }
    
    /* 闂佹彃锕ラ弬渚€骞嶉埀顒勫嫉婢跺﹦鍞ㄩ柛?*/
    if (bank->genes) {
        for (size_t i = 0; i < bank->gene_count; i++) {
            quantum_gene_destroy(bank->genes[i]);
        }
        free(bank->genes);
    }
    
    /* 闂佹彃锕ラ弬渚€宕洪崫鍕閹煎瓨鎸剧划銊╁几閸曨亞绉?*/
    free(bank);
}

int quantum_gene_bank_add_gene(QGeneBank* bank, QGene* gene) {
    if (!bank || !gene) {
        return 0;
    }
    
    /* 婵☆偀鍋撻柡灞诲劜濡叉悂宕ラ敃鈧崙锛勨偓娑櫭﹢顏堝触鐎涙湆闁糕晛鎼ú?*/
    for (size_t i = 0; i < bank->gene_count; i++) {
        if (strcmp(bank->genes[i]->id, gene->id) == 0) {
            /* 闁哄洦瀵у畷鏌ユ偝閻楀牊绠掗柛鈺佹惈濞?*/
            quantum_gene_destroy(bank->genes[i]);
            bank->genes[i] = gene;
            return 1;
        }
    }
    
    /* 闁圭鏅涢惈宥夊春閸濆嫭绀堥柡浣瑰缁?*/
    QGene** new_genes = (QGene**)realloc(bank->genes, 
                                       (bank->gene_count + 1) * sizeof(QGene*));
    if (!new_genes) {
        return 0;
    }
    
    bank->genes = new_genes;
    bank->genes[bank->gene_count] = gene;
    bank->gene_count++;
    
    return 1;
}

QGene* quantum_gene_bank_find_gene(QGeneBank* bank, const char* id) {
    if (!bank || !id) {
        return NULL;
    }
    
    /* 闁哄被鍎叉竟姗€宕洪崫鍕 */
    for (size_t i = 0; i < bank->gene_count; i++) {
        if (strcmp(bank->genes[i]->id, id) == 0) {
            return bank->genes[i];
        }
    }
    
        return NULL;
    }
    
int quantum_gene_bank_remove_gene(QGeneBank* bank, const char* id) {
    if (!bank || !id || bank->gene_count == 0) {
        return 0;
    }
    
    /* 闁哄被鍎叉竟姗€宕洪崫鍕缂佷究鍨圭槐?*/
    size_t index = bank->gene_count;
    for (size_t i = 0; i < bank->gene_count; i++) {
        if (strcmp(bank->genes[i]->id, id) == 0) {
            index = i;
            break;
        }
    }
    
    /* 濠碘€冲€归悘澶愬嫉椤忓懎顥濋柛鎺撴緲閻斺偓闁?*/
    if (index == bank->gene_count) {
        return 0;
    }
    
    /* 闂佹彃锕ラ弬渚€宕洪崫鍕 */
    quantum_gene_destroy(bank->genes[index]);
    
    /* 缂佸顕ф慨鈺呭极閹殿喚鐭嬮柛蹇撳暟缁€?*/
    for (size_t i = index; i < bank->gene_count - 1; i++) {
        bank->genes[i] = bank->genes[i + 1];
    }
    
    /* 闁哄洤鐡ㄩ弻濠囧春閸濆嫭绀堥悹浣插墲閺?*/
    bank->gene_count--;
    
    return 1;
} 
