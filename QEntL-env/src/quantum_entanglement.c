/**
 * 闂佹彃绻愰悺娆戠棯閻樼數鐐婃俊顖椻偓铏仴閻庡湱鍋熼獮鍥棘閸ワ附顐?- 缂佺姭鍋撻柛鏍ㄧ墱婢? * 
 * @闁哄倸娲ｅ▎? quantum_entanglement.c
 * @闁硅绻楅崼? 閻庡湱鍋熼獮鍥煂韫囨挾鎽嶇紒鍓уХ缁卞爼鎯冮崟顐ゅ敤闁哄牜鍓氶幖閿嬫媴濠婂啫姣愰柡? * @闁绘鐗婂﹢? 1.0
 */

#include "quantum_entanglement.h"
#include "quantum_gene.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* -------------------- 闂佹彃绻愰悺娆戠棯閻樼數鐐婇柛鈺冨劋濠€浼村箼瀹ュ嫮绋婇柛鎴ｅГ閺?-------------------- */

QEntanglement* quantum_entanglement_create(const char* id, QState* state1, QState* state2, double strength) {
    if (!id || !state1 || !state2 || strength < 0.0 || strength > 1.0) {
        return NULL;
    }
    
    QEntanglement* entanglement = (QEntanglement*)malloc(sizeof(QEntanglement));
    if (!entanglement) {
        return NULL;
    }
    
    entanglement->id = strdup(id);
    if (!entanglement->id) {
        free(entanglement);
        return NULL;
    }
    
    entanglement->state1 = state1;
    entanglement->state2 = state2;
    entanglement->strength = strength;
    entanglement->type = ENTANGLEMENT_TYPE_BELL_PAIR; // 濮掓稒顭堥鑽ょ尵鐠囪尙鈧?    entanglement->fidelity = 1.0; // 濮掓稒顭堥缁樼┍濠靛牊鍩傞幖?    
    // 闁哄洤鐡ㄩ弻濠囨煂韫囨挾鎽嶉柟顑胯兌濞堟垹鐥悩鐢电倞闁稿繐纾柈?    quantum_state_add_entanglement(state1, entanglement);
    quantum_state_add_entanglement(state2, entanglement);
    
    // 閻犱礁澧介悿鍡欎沪閻愮补鍋撹閻栵絿鎷嬮幍顔剧湴缂傚倻濮锋慨鎼佸箑?    char strength_str[20];
    sprintf(strength_str, "%.2f", strength);
    quantum_state_set_property(state1, "entangled", "true");
    quantum_state_set_property(state1, "entanglement_strength", strength_str);
    quantum_state_set_property(state2, "entangled", "true");
    quantum_state_set_property(state2, "entanglement_strength", strength_str);
    
    return entanglement;
}

void quantum_entanglement_destroy(QEntanglement* entanglement) {
    if (!entanglement) {
        return;
    }
    
    // 婵炴挸鎳樺▍搴ㄦ煂韫囨挾鎽嶉柟顑挎閼垫垿鎯冮崟顓犵湴缂傚倻濮撮惈姗€骞€?    if (entanglement->state1) {
        quantum_state_set_property(entanglement->state1, "entangled", "false");
        quantum_state_set_property(entanglement->state1, "entanglement_strength", "0.0");
    }
    
    if (entanglement->state2) {
        quantum_state_set_property(entanglement->state2, "entangled", "false");
        quantum_state_set_property(entanglement->state2, "entanglement_strength", "0.0");
    }
    
    // 闂佹彃锕ラ弬涓
    if (entanglement->id) {
        free(entanglement->id);
    }
    
    // 闂佹彃锕ラ弬浣虹磼閹惧鈧垱鎷?    free(entanglement);
}

int quantum_entanglement_set_type(QEntanglement* entanglement, EntanglementType type) {
    if (!entanglement) {
        return 0;
    }
    
    entanglement->type = type;
    return 1;
}

double quantum_entanglement_get_strength(QEntanglement* entanglement) {
    if (!entanglement) {
        return 0.0;
    }
    
    return entanglement->strength;
}

int quantum_entanglement_adjust_strength(QEntanglement* entanglement, double strength) {
    if (!entanglement || strength < 0.0 || strength > 1.0) {
        return 0;
    }
    
    entanglement->strength = strength;
    
    // 闁哄洤鐡ㄩ弻濠囨煂韫囨挾鎽嶉柟顑胯兌濞堟垹鐥悩鐢电倞鐎殿喖鎼€瑰磭浠﹂悙绮瑰亾?    char strength_str[20];
    sprintf(strength_str, "%.2f", strength);
    
    if (entanglement->state1) {
        quantum_state_set_property(entanglement->state1, "entanglement_strength", strength_str);
    }
    
    if (entanglement->state2) {
        quantum_state_set_property(entanglement->state2, "entanglement_strength", strength_str);
    }
    
    return 1;
}

QState* quantum_entanglement_measure(QEntanglement* entanglement, int measure_state1) {
    if (!entanglement) {
        return NULL;
    }
    
    // 缁绢収鍠栭悾鍓ф啺娴ｅ湱銈撮梺鎻掔箳濞堟垿鎮╅懜纰樺亾?    QState* state_to_measure = measure_state1 ? entanglement->state1 : entanglement->state2;
    QState* other_state = measure_state1 ? entanglement->state2 : entanglement->state1;
    
    if (!state_to_measure || !other_state) {
        return NULL;
    }
    
    // 闁圭瑳鍡╂斀婵炴潙顑夐崳?    QState* measured_state = quantum_state_measure(state_to_measure);
    if (!measured_state) {
        return NULL;
    }
    
    // 闁兼儳鍢茶ぐ鍥圭€ｎ喖娅ょ紓浣规尰閻?    const char* result = quantum_state_get_property(measured_state, "result");
    if (!result) {
        quantum_state_destroy(measured_state);
        return NULL;
    }
    
    // 闁哄秷顫夊畵浣虹棯閻樼數鐐婇柛蹇撶－闁挳宕仦鍓с偞闂佹彃绻掔划銊╁几濠婂啫顨涢柛婵嗙Т瑜扮喐绋夐埀顒佺▔椤忓棗笑闁?    if (entanglement->strength > 0.5) { // 闁告瑯浜濆﹢渚€宕烽妸銊ュ枙濠㈠墎鍠庡閬嶆儍閸曨厾鐪扮紓鍌滃С缁楀懘骞嶅鍡樼畳闁哄嫬瀛╁Ο澶愬礂鐎圭姳绮?
        // 缂佺姭鍋撻柛鏍ㄧ墱濞堟垹鐥悩鐢电倞闁轰礁鐗嗙花鏌ユ晬濮橆剙缍楀☉鎾亾濞戞搩浜炴慨鎼佸箑娴ｅ厜鍋撶紒妯恍﹀☉鎾冲缁佹挳鏌岃箛鏇犳尝闁哄绮庡ù澶愬礂?        if (strcmp(result, "0") == 0) {
            // 濠碘€冲€归悘澶娒圭€ｎ喖娅ょ紓浣规尰閻忓绋夌花?闁村嫧鏅槐婵嬪矗閿旇法顏卞☉鎿冧簽婵悂骞€娴ｉ鐦嶉柛濠冨劤閹粍绂嶅?闁?            other_state->alpha = 1.0;
            other_state->beta = 0.0;
        } else {
            // 濠碘€冲€归悘澶娒圭€ｎ喖娅ょ紓浣规尰閻忓绋夌花?闁村嫧鏅槐婵嬪矗閿旇法顏卞☉鎿冧簽婵悂骞€娴ｉ鐦嶉柛濠冨劤閹粍绂嶅?闁?            other_state->alpha = 0.0;
            other_state->beta = 1.0;
        }
        
        // 閻犱礁澧介悿鍡涙儎缁嬪灝褰犻悘鐐靛仦閳?        quantum_state_set_property(other_state, "correlated_measurement", "true");
        quantum_state_set_property(other_state, "correlated_with", measured_state->name);
    }
    
    // 婵炴潙顑夐崳娲触鎼达絿澹冮柛褍绻掔猾鍌滅磽?    quantum_entanglement_destroy(entanglement);
    
    return measured_state;
}

QEntanglement* quantum_entanglement_create_bell_pair(const char* id, QState* state1, QState* state2) {
    if (!id || !state1 || !state2) {
        return NULL;
    }
    
    // 闁告帗绋戠紓鎾舵嫻濠靛棛姣滈悗闈涙贡缁倻绱?    QEntanglement* entanglement = quantum_entanglement_create(id, state1, state2, 1.0);
    if (!entanglement) {
        return NULL;
    }
    
    // 閻犱礁澧介悿鍡欐嫻濠靛棛姣滈悗闈涙贡鐞氼偊宕?    entanglement->type = ENTANGLEMENT_TYPE_BELL_PAIR;
    
    // 閻犱礁澧介悿鍡涙煂韫囨挾鎽嶉柟顑跨閻﹢骞€?    quantum_state_set_property(state1, "entanglement_type", "bell_pair");
    quantum_state_set_property(state2, "entanglement_type", "bell_pair");
    
    // 闁告帗绋戠紓鎾舵嫻濠靛棛姣滈柟?(|00闁?+ |11闁?/闁?
    // 閺夆晜鐟╅崳閿嬬閸涢偊鍟庣紓鍐惧枟閻栵絿鎷嬬敮顔剧閻庡湱鍋ゅ顖炴煂韫囨挾鎽嶉柟顑胯兌濞堟垿骞愰姘辩暯闁革负鍔庡﹢锛勨偓鍦仱閸ｈ櫣鈧稒鍔楅柈瀵哥磼閻旀儼鍘柟闈涚У濠€渚€骞囪箛搴ｇ枀
    quantum_state_set_property(state1, "bell_state", "true");
    quantum_state_set_property(state2, "bell_state", "true");
    
    return entanglement;
}

/* -------------------- 缂佸墽濮风槐鍫曟焻濮樻湹澹曢柟鍨С缂嶆棃宕欓懞銉︽ -------------------- */

EntanglementChannel* quantum_entanglement_channel_create(const char* id) {
    if (!id) {
        return NULL;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)malloc(sizeof(EntanglementChannel));
    if (!channel) {
        return NULL;
    }
    
    channel->id = strdup(id);
    if (!channel->id) {
        free(channel);
        return NULL;
    }
    
    channel->pairs = NULL;
    channel->pair_count = 0;
    channel->coherence_time = 1000.0; // 濮掓稒顭堥?缂?    
    return channel;
}

void quantum_entanglement_channel_destroy(EntanglementChannel* channel) {
    if (!channel) {
        return;
    }
    
    // 闂佹彃锕ラ弬渚€骞嶉埀顒勫嫉婢跺瞼鐪扮紓鍌滃Т椤?    EntanglementPair* current = channel->pairs;
    while (current) {
        EntanglementPair* next = current->next;
        
        // 濞戞挸绉归崳鎾绩閸撗呯湴缂傚倻濮靛﹢浼寸叕椤愵剛绀夐柛銉уС鐠愮喖宕ｉ婵嗗幋閻炴凹鍋勯崣鐐閺嶎偆娉㈤柡瀣缁扁晠鎮?        free(current);
        current = next;
    }
    
    // 闂佹彃锕ラ弬涓
    if (channel->id) {
        free(channel->id);
    }
    
    // 闂佹彃锕ラ弬渚€鏌呭鏈靛缂備焦鎸婚悗?    free(channel);
}

int quantum_entanglement_channel_add(EntanglementChannel* channel, QEntanglement* entanglement) {
    if (!channel || !entanglement) {
        return 0;
    }
    
    // 闁告帗绋戠紓鎾诲棘閹殿喗鐣辩紒鍓уХ缁卞墎鈧數顢婃俊顓㈡倷?    EntanglementPair* pair = (EntanglementPair*)malloc(sizeof(EntanglementPair));
    if (!pair) {
        return 0;
    }
    
    pair->entanglement = entanglement;
    
    // 婵烇綀顕ф慨鐐哄礆娴煎瓨鎳犻悶娑栧妼閵囨棃鏌?    pair->next = channel->pairs;
    channel->pairs = pair;
    channel->pair_count++;
    
    return 1;
}

int quantum_entanglement_channel_remove(EntanglementChannel* channel, const char* entanglement_id) {
    if (!channel || !entanglement_id || !channel->pairs) {
        return 0;
    }
    
    EntanglementPair* current = channel->pairs;
    EntanglementPair* prev = NULL;
    
    // 闁哄被鍎叉竟妯兼啺娴ｇ洅鈺呮⒔閵堝洦鐣辩紒鍓уХ缁卞墎鈧?    while (current) {
        if (strcmp(current->entanglement->id, entanglement_id) == 0) {
            // 濞寸姴閰ｉ幗鑲╂偘閵娿倛鍘紒澶婎煼濞?            if (prev) {
                prev->next = current->next;
            } else {
                channel->pairs = current->next;
            }
            
            // 闂佹彃锕ラ弬渚€鎳為崒婊冧化闁挎稑鐗呯粭澶愭煂婵犲啯鏉圭紒鍓уХ缁卞爼寮甸鍐叐闁?            free(current);
            channel->pair_count--;
            return 1;
        }
        
        prev = current;
        current = current->next;
    }
    
    return 0; // 闁哄牜浜濇竟姗€宕?}

QEntanglement* quantum_entanglement_channel_find(EntanglementChannel* channel, const char* entanglement_id) {
    if (!channel || !entanglement_id) {
        return NULL;
    }
    
    EntanglementPair* current = channel->pairs;
    
    // 闂侇剙绉村濠氬蓟閵夛箑顥?
    while (current) {
        if (strcmp(current->entanglement->id, entanglement_id) == 0) {
            return current->entanglement;
        }
        current = current->next;
    }
    
    return NULL; // 闁哄牜浜濇竟姗€宕?}

int quantum_entanglement_channel_apply_gene(EntanglementChannel* channel, QGene* gene) {
    if (!channel || !gene) {
        return 0;
    }
    
    // 闁告瑯浜濆﹢浣该洪弰蹇曗攬闁汇劌瀚悢鈧柛銉уУ婢х娀鎳楅挊澶屽畨闁?    if (gene->expression.is_active != 1) {
        return 0;
    }
    
    // 闁兼儳鍢茶ぐ鍥春閸濆嫭绀堢紒顐ヮ嚙閻庨浠﹂悙绮瑰亾?    const char* gene_type = quantum_gene_get_property(gene, "channel_effect");
    if (!gene_type) {
        return 0; // 婵炲备鍓濆﹢渚€鏌呭鏈靛闁轰礁鐗嗙花?    }
    
    // 閹煎瓨姊婚弫銈夊春閸濆嫭绀堥柡浣哥墕缁?    if (strcmp(gene_type, "coherence_enhance") == 0) {
        // 濠⒀呭仜瀹搁亶鎯勭粙鍨彙闁哄啫鐖煎Λ?        channel->coherence_time *= (1.0 + gene->expression.strength);
        return 1;
    } 
    else if (strcmp(gene_type, "strength_boost") == 0) {
        // 闁圭粯鍔曞畷宀勫箥閳ь剟寮垫径宀€鐪扮紓鍌滃Т瀹歌鲸鎯?        EntanglementPair* current = channel->pairs;
        while (current) {
            double new_strength = current->entanglement->strength * (1.0 + gene->expression.strength * 0.5);
            if (new_strength > 1.0) new_strength = 1.0;
            
            quantum_entanglement_adjust_strength(current->entanglement, new_strength);
            current = current->next;
        }
        return 1;
    }
    
    return 0; // 濞戞挸绉甸弫顕€骞愭担鐑樼暠闁糕晛鎼ú婊呯尵鐠囪尙鈧?}

QEntanglement* quantum_entanglement_swap(QEntanglement* entanglement1, QEntanglement* entanglement2, const char* new_id) {
    if (!entanglement1 || !entanglement2 || !new_id) {
        return NULL;
    }
    
    // 濡ょ姴鐭侀惁澶愬矗椤栨瑤绨伴柟绗涘棭鏀藉ù婧垮€栧畷?    if (entanglement1->state2 != entanglement2->state1) {
        return NULL; // 濞戞挶鍊撻柌婊呯棯閻樼數鐐婇煫鍥ф嚇閵嗗繘宕楅崣姗€鐓╁☉鎾亾濞戞搩浜欓懙鎴︽⒒鐎涙ǚ鍋?    }
    
    // 闁兼儳鍢茶ぐ鍥╂啺娴ｇ晫绠鹃柟鎭掑劤濞堟垶绋夐妶鍕殝濠㈣埖鐗犻崕鎾箑?    QState* state1 = entanglement1->state1;
    QState* state2 = entanglement2->state2;
    
    // 閻犱緤绱曢悾濠氬棘閹殿喚鐪扮紓鍌滃Х濞堟垵顕ｉ崫鍕唺闁挎稑鐗忛悾婵嬪礌閺嵮呮澖闁绘粌搴滅槐浼村矗閺嶏箒鈷堝☉鎿冧簻鐢偅鎱ㄧ€ｎ剛鐪扮紓鍌滃Х濞堟垵顕ｉ崫鍕唺濞戞梹顭囪ⅶ闁?    double new_strength = entanglement1->strength * entanglement2->strength;
    
    // 闁告帗绋戠紓鎾诲棘閹殿喗鐣辩紒鍓уХ缁?    QEntanglement* new_entanglement = quantum_entanglement_create(new_id, state1, state2, new_strength);
    if (!new_entanglement) {
        return NULL;
    }
    
    // 闁告瑯鍨禍鎺楁焻婢跺顏ラ梺搴撳亾婵絼绀佺敮顐﹀嫉婢跺瞼鐪扮紓?    // quantum_entanglement_destroy(entanglement1);
    // quantum_entanglement_destroy(entanglement2);
    
    return new_entanglement;
} 
