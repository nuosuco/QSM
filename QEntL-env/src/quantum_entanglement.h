/**
 * 闂佹彃绻愰悺娆戠棯閻樼數鐐婃俊顖椻偓铏仴濠㈣泛鐡ㄩ弸鍐╃?- 缂佺姭鍋撻柛鏍ㄧ墱婢?
 * 
 * @闁哄倸娲ｅ▎? quantum_entanglement.h
 * @闁硅绻楅崼? 閻庤鐭粻鐔兼煂韫囨挾鎽嶇紒鍓уХ缁卞爼鎯冮崟顐ゅ敤闁哄牜鍓涚划銊╁几閸曨偅瀚查柟鍨С缂嶆棃宕欓懞銉︽
 * @闁绘鐗婂﹢? 1.0
 */

#ifndef QENTL_QUANTUM_ENTANGLEMENT_H
#define QENTL_QUANTUM_ENTANGLEMENT_H

#include <stdint.h>
#include <stdlib.h>
#include <complex.h>
#include "quantum_state.h" // 闁告牕鎳庨幆鍫ユ煂韫囨挾鎽嶉柣妯垮煐閳ь兛绀侀悾鐐▕?

/* 闁告挸绉撮幃婊勭珶閻楀牊顫?*/
struct QGene;
typedef struct QGene QGene;

/**
 * 缂佸墽濮风槐鍓佺尵鐠囪尙鈧?
 */
typedef enum {
    ENTANGLEMENT_TYPE_BELL_PAIR,  // 閻犳劖绻傞惃鐢碘偓?
    ENTANGLEMENT_TYPE_GHZ,        // GHZ闁?
    ENTANGLEMENT_TYPE_W_STATE,    // W闁?
    ENTANGLEMENT_TYPE_CLUSTER,    // 缂併劌娲﹂埀?
    ENTANGLEMENT_TYPE_CUSTOM      // 闁煎浜滈悾鐐▕婢跺瞼鐪扮紓鍌滃Х鐞氼偊宕?
} EntanglementType;

/**
 * 闂佹彃绻愰悺娆戠棯閻樼數鐐婄紓浣规尰閻?
 */
typedef struct QEntanglement {
    char* id;                    // 缂佸墽濮风槐绂滵
    QState* state1;              // 缂佹鍏涚粩瀛樼▔椤忓棛鐪扮紓鍌滃У閳?
    QState* state2;              // 缂佹鍏涚花鈺傜▔椤忓棛鐪扮紓鍌滃У閳?
    double strength;             // 缂佸墽濮风槐璺侯嚕閸濆嫬顔婇柨?.0-1.0闁?
    EntanglementType type;       // 缂佸墽濮风槐鍓佺尵鐠囪尙鈧?
    double fidelity;             // 缂佸墽濮风槐鑸电┍濠靛牊鍩傞幖?
} QEntanglement;

/**
 * 缂佸墽濮风槐鍓佲偓闈涙贡缁劑寮?
 */
typedef struct EntanglementPair {
    QEntanglement* entanglement; // 缂佸墽濮风槐鍓佲偓鍦仒缁?
    struct EntanglementPair* next; // 濞戞挸顑勭粩瀛樼▔椤忓棛鐪扮紓鍌滃Т椤?
} EntanglementPair;

/**
 * 缂佸墽濮风槐鍫曟焻濮樻湹澹曠紓浣规尰閻?
 */
typedef struct {
    char* id;                    // 闂侇偅宀告禍缍
    EntanglementPair* pairs;     // 缂佸墽濮风槐鍓佲偓闈涚秺閹借偐鎮?
    size_t pair_count;           // 缂佸墽濮风槐鍓佲偓浣冾潐閺嗙喖鏌?
    double coherence_time;       // 闁烩晝顭堥崗閬嶅籍閸洘锛熼柨娑樼墛椤曠姷绮旈幒鐐电
} EntanglementChannel;

/* -------------------- 闂佹彃绻愰悺娆戠棯閻樼數鐐婇柛鈺冨劋濠€浼村箼瀹ュ嫮绋婇柛鎴ｅГ閺?-------------------- */

/**
 * 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶇紒鍓уХ缁?
 * 
 * @param id 缂佸墽濮风槐绂滵
 * @param state1 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姈閳?
 * @param state2 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姈閳?
 * @param strength 缂佸墽濮风槐璺侯嚕閸濆嫬顔婇柨?.0-1.0闁?
 * @return 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚涢柨娑樿嫰閵囨垹鎷归妷銊х闁搞儲鎱稶LL
 */
QEntanglement* quantum_entanglement_create(const char* id, QState* state1, QState* state2, double strength);

/**
 * 闂佸簱鍋撴慨锝勭窔閸ｈ櫣鈧稒鍔楃猾鍌滅磽?
 * 
 * @param entanglement 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚?
 */
void quantum_entanglement_destroy(QEntanglement* entanglement);

/**
 * 閻犱礁澧介悿鍡欑棯閻樼數鐐婄紒顐ヮ嚙閻?
 * 
 * @param entanglement 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚?
 * @param type 缂佸墽濮风槐鍓佺尵鐠囪尙鈧?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_entanglement_set_type(QEntanglement* entanglement, EntanglementType type);

/**
 * 闁兼儳鍢茶ぐ鍥╃棯閻樼數鐐婄€殿喖鎼€?
 * 
 * @param entanglement 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚?
 * @return 缂佸墽濮风槐璺侯嚕閸濆嫬顔?
 */
double quantum_entanglement_get_strength(QEntanglement* entanglement);

/**
 * 閻犲鍟弳锝囩棯閻樼數鐐婄€殿喖鎼€?
 * 
 * @param entanglement 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚?
 * @param strength 闁哄倹澹嗗▓鎴犵棯閻樼數鐐婄€殿喖鎼€?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_entanglement_adjust_strength(QEntanglement* entanglement, double strength);

/**
 * 婵炴潙顑夐崳娲煂韫囨挾鎽嶇紒鍓уХ缁?
 * 
 * @param entanglement 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚?
 * @param measure_state1 闁哄嫷鍨伴幆浣该圭€ｎ喖娅ょ紒妤婂厸缁斿瓨绋夐鍛亾?
 * @return 閻炴凹鍋呯粊鎾煂韫囨洘鐣遍梺鎻掔箰閻℃瑩骞€娓氬﹦绀夊鎯扮簿鐟欙附娼婚弬鎸庣NULL
 */
QState* quantum_entanglement_measure(QEntanglement* entanglement, int measure_state1);

/**
 * 闁告帗绋戠紓鎾舵嫻濠靛棛姣滈悗闈涙贡缁倻绱?
 * 
 * @param id 缂佸墽濮风槐绂滵
 * @param state1 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姈閳?
 * @param state2 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姈閳?
 * @return 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚涢柨娑樿嫰閵囨垹鎷归妷銊х闁搞儲鎱稶LL
 */
QEntanglement* quantum_entanglement_create_bell_pair(const char* id, QState* state1, QState* state2);

/* -------------------- 缂佸墽濮风槐鍫曟焻濮樻湹澹曢柟鍨С缂嶆棃宕欓懞銉︽ -------------------- */

/**
 * 闁告帗绋戠紓鎾剁棯閻樼數鐐婇梺顐ｅ哺娴?
 * 
 * @param id 闂侇偅宀告禍缍
 * @return 闂侇偅宀告禍楣冨箰閸ヮ剚瀚涢柨娑樿嫰閵囨垹鎷归妷銊х闁搞儲鎱稶LL
 */
EntanglementChannel* quantum_entanglement_channel_create(const char* id);

/**
 * 闂佸簱鍋撴慨锝勮兌缁倻绱撻悩鐑╁亾濮樻湹澹?
 * 
 * @param channel 闂侇偅宀告禍楣冨箰閸ヮ剚瀚?
 */
void quantum_entanglement_channel_destroy(EntanglementChannel* channel);

/**
 * 闁告碍鍨块埀顒佸哺娴滄儳菐鐠囨彃顫ｇ紒鍓уХ缁?
 * 
 * @param channel 闂侇偅宀告禍楣冨箰閸ヮ剚瀚?
 * @param entanglement 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_entanglement_channel_add(EntanglementChannel* channel, QEntanglement* entanglement);

/**
 * 濞寸姴閰ｉ埀顒佸哺娴滃墽绮旀繝姘彑缂佸墽濮风槐?
 * 
 * @param channel 闂侇偅宀告禍楣冨箰閸ヮ剚瀚?
 * @param entanglement_id 缂佸墽濮风槐绂滵
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_entanglement_channel_remove(EntanglementChannel* channel, const char* entanglement_id);

/**
 * 闁哄被鍎叉竟姗€鏌呭鏈靛濞戞搩鍘惧▓鎴犵棯閻樼數鐐?
 * 
 * @param channel 闂侇偅宀告禍楣冨箰閸ヮ剚瀚?
 * @param entanglement_id 缂佸墽濮风槐绂滵
 * @return 缂佸墽濮风槐鍫曞箰閸ヮ剚瀚涢柨娑樺缁楀鈧稒锚濠€顏呮交閺傛寧绀€NULL
 */
QEntanglement* quantum_entanglement_channel_find(EntanglementChannel* channel, const char* entanglement_id);

/**
 * 閻忓繐妫楅悢鈧柛銉уТ缁ㄦ煡鎮介妸銉ョ厒缂佸墽濮风槐鍫曟焻濮樻湹澹?
 * 
 * @param channel 闂侇偅宀告禍楣冨箰閸ヮ剚瀚?
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_entanglement_channel_apply_gene(EntanglementChannel* channel, QGene* gene);

/**
 * 闁圭瑳鍡╂斀缂佸墽濮风槐鑸电閵堝棗搴婇柟鍨С缂?
 * 
 * @param entanglement1 缂佹鍏涚粩瀛樼▔椤忓棛鐪扮紓?
 * @param entanglement2 缂佹鍏涚花鈺傜▔椤忓棛鐪扮紓?
 * @param new_id 闁哄倹澹嗙猾鍌滅磽閻曠儭
 * @return 闁哄倹澹嗗▓鎴犵棯閻樼數鐐婇柨娑樿嫰閵囨垹鎷归妷銊х闁搞儲鎱稶LL
 */
QEntanglement* quantum_entanglement_swap(QEntanglement* entanglement1, QEntanglement* entanglement2, const char* new_id);

#endif /* QENTL_QUANTUM_ENTANGLEMENT_H */ 
