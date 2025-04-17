/**
 * QEntL闂佹彃绻愰悺娆撴偐閼哥鍋撴担鎼炰粓闁哄倸娲ｅ▎? * 
 * 闂佹彃绻愰悺娆撳春閸濆嫭绀堢紓鍌涚墱閻? QG-CORE-STATE-HEADER-A1B0
 * 
 * @闁哄倸娲ｅ▎? quantum_state.h
 * @闁硅绻楅崼? 閻庤鐭粻鐔兼煂韫囨挾鎽嶉柟顑胯兌濞堟垿宕洪悜妯绘嫳缂備焦鎸婚悗顖炲椽鐏炵偓鎯欏ù锝嗙矊閸ら亶寮? * @濞达絾绮忛埀? QEntL闁哄秶顭堢缓鎯ь嚕閳ь剟宕ｉ幋婵囩闂? * @闁哄啨鍎插﹢? 2024-05-15
 * @闁绘鐗婂﹢? 1.0
 * 
 * 闂佹彃绻愰悺娆戠棯閻樼數鐐婂ǎ鍥ｅ墲娴?
 * - 婵縿鍊栬啯闁秆勵殜缁垳鎷嬮妶鍜佹П濞存粌瀛╃缓鍝劽洪懡銈呅﹂柟顑跨筏缁辨繈鎳楅崐鐔锋闁告柣鍔屽顒佺▔鎼淬劌娅ら悗娑欏姉缁倻绱撻悩鐢电Ч缂備焦绮嶉悗顖氼嚈? * - 闂佹彃绻愰悺娆撴偐閼哥鍋撴担钘夋闁告柣鍔岀€垫﹢宕ラ锕€娅ら悗娑欏姇閻斺偓闁搞儳濮风槐顏堟儘娴ｅ憡瀚查梺鎻掔箰閻℃瑧鐥悩鐢电倞濞ｅ浄绻濇禍? * - 闁煎疇濮ら悧鎾箲椤旇法绠ラ悶娑樼灱楠炲棙鏅堕崘顓炴闂侇偄鍊哥花鑼嫬閸愨晜娈婚梺鎻掔箰閻℃瑥袙閺冨倸顥楀璺哄閹﹪鎳楅挊澶婎潝
 */

#ifndef QENTL_QUANTUM_STATE_H
#define QENTL_QUANTUM_STATE_H

#include <stdlib.h>
#include <stdint.h>
#include <complex.h>  /* 缁绢収鍠曠换姘跺礌閸涱厽鍎撳璺虹У閺嗙喖寮ㄩ娑樼槷 */

/**
 * 闁告挸绉撮幃婊勭珶閻楀牊顫?
 */
typedef struct QGene QGene;
typedef struct QEntanglement QEntanglement;

/**
 * 闂佹彃绻愰悺娆撴偐閼哥鍋撴担楦款潶闁? */
typedef enum {
    QSTATE_BASIC,        /* 闁糕晞娅ｉ、鍛存偐閼哥鍋?*/
    QSTATE_SUPERPOSITION, /* 闁告瑧濮存慨鐐哄箑?*/
    QSTATE_ENTANGLED,     /* 缂佸墽濮风槐鍫曞箑?*/
    QSTATE_MEASURED      /* 鐎圭寮剁粊鎾煂韫囨洖笑闁?*/
} QStateType;

/**
 * 闂佹彃绻愰悺娆撴偐閼哥鍋? */
typedef struct QState {
    char* name;                   /* 闁绘鍩栭埀顑跨閹洜绮?*/
    QStateType type;              /* 闁绘鍩栭埀顑胯兌鐞氼偊宕?*/
    void* state_data;             /* 闁绘鍩栭埀顑跨劍閺嗙喖骞戦鍡欑闁哄秷顫夊畵浣虹尵鐠囪尙鈧兘寮垫径澶岀憹闁告艾鐬煎▓鎴犵磼閹惧鈧?*/
    QGene* quantum_gene;          /* 闂佹彃绻愰悺娆撳春閸濆嫭绀堥柡宥呮穿椤?*/
    QEntanglement** entanglements; /* 闂佹彃绻愰悺娆戠棯閻樼數鐐婇柡浣瑰缁?*/
    size_t entanglement_count;    /* 缂佸墽濮风槐鍫曞极娴兼潙娅?*/
    char** properties;            /* 閻忕偟鍋為埀顑啯鍊崇紒澶屽閺嗙喓绱?*/
    char** property_values;       /* 閻忕偟鍋為埀顑啠鍋撻崗鍏兼缂?*/
    size_t property_count;        /* 閻忕偟鍋為埀顑嫭娈堕梺?*/
    double complex alpha;         /* 闂佹彃绻愰悺娆徯掗弮鍌氼棗|0闁村嫧鏅涢悢鈧柟顑跨劍鐏忕喖鐛?*/
    double complex beta;          /* 闂佹彃绻愰悺娆徯掗弮鍌氼棗|1闁村嫧鏅涢悢鈧柟顑跨劍鐏忕喖鐛?*/
} QState;

/**
 * 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柣妯垮煐閳? * 
 * @param name 闁绘鍩栭埀顑跨閹洜绮? * @return 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂佽棄鐗炵槐婵囧緞鏉堫偉袝閺夆晜鏌ㄥú鏈淯LL
 */
QState* quantum_state_create(const char* name);

/**
 * 闂佸簱鍋撴慨锝勭窔閸ｈ櫣鈧稒鍔楁慨鎼佸箑? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? */
void quantum_state_destroy(QState* state);

/**
 * 閻犱礁澧介悿鍡涙偐閼哥鍋撴担鍝ユ剑闁? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? * @param name 閻忕偟鍋為埀顑啯鍊崇紒? * @param value 閻忕偟鍋為埀顑啠鍋? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_state_set_property(QState* state, const char* name, const char* value);

/**
 * 闁兼儳鍢茶ぐ鍥偐閼哥鍋撴担鍝ユ剑闁? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? * @param name 閻忕偟鍋為埀顑啯鍊崇紒? * @return 閻忕偟鍋為埀顑啠鍋撶涵椋庣濞戞挸绉撮悺銊╁捶閵娿劎绠查柛銉︽叿ULL
 */
const char* quantum_state_get_property(QState* state, const char* name);

/**
 * 閹煎瓨姊婚弫銈夋煂韫囨挾鎽嶉柛鈺佹惈濞? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? * @param gene 闂佹彃绻愰悺娆撳春閸濆嫭绀堥柟绋挎喘閹? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_state_apply_gene(QState* state, QGene* gene);

/**
 * 婵烇綀顕ф慨鐐烘煂韫囨挾鎽嶇紒鍓уХ缁? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? * @param entanglement 闂佹彃绻愰悺娆戠棯閻樼數鐐婇柟绋挎喘閹? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_state_add_entanglement(QState* state, QEntanglement* entanglement);

/**
 * 闁告帗绋戠紓鎾诲矗閻樻彃顫ｉ柟? * 
 * @param name 闁绘鍩栭埀顑跨閹洜绮? * @param states 闁糕晞娅ｉ、鍛村箑娴ｈ娈剁紓? * @param amplitudes 闁瑰壊鍨扮粻娆撳极閹殿喚鐭?
 * @param count 闁绘鍩栭埀顑跨劍閺嗙喖鏌? * @return 闁告瑧濮存慨鐐哄箑娴ｇ懓鐦归梺钘夌墳缁辨繃寰勬潏顐バ曢弶鈺傛煥濞叉湝ULL
 */
QState* quantum_state_create_superposition(const char* name, QState** states, 
                                          double* amplitudes, size_t count);

/**
 * 闁告帗绋戠紓鎾剁棯閻樼數鐐婇柟? * 
 * @param name 闁绘鍩栭埀顑跨閹洜绮? * @param state1 缂佹鍏涚粩瀛樼▔椤忓棗笑闁? * @param state2 缂佹鍏涚花鈺傜▔椤忓棗笑闁? * @param strength 缂佸墽濮风槐璺侯嚕閸濆嫬顔?(0.0-1.0)
 * @return 缂佸墽濮风槐鍫曞箑娴ｇ懓鐦归梺钘夌墳缁辨繃寰勬潏顐バ曢弶鈺傛煥濞叉湝ULL
 */
QState* quantum_state_create_entangled(const char* name, QState* state1, 
                                      QState* state2, double strength);

/**
 * 婵炴潙顑夐崳娲煂韫囨挾鎽嶉柣妯垮煐閳? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? * @return 婵炴潙顑夐崳铏圭磼閹惧浜柣妯垮煐閳ь兛绶ょ槐婵囧緞鏉堫偉袝閺夆晜鏌ㄥú鏈淯LL
 */
QState* quantum_state_measure(QState* state);

/**
 * 闁稿繐顑夊▓鏇㈡煂韫囨挾鎽嶉柣妯垮煐閳? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? * @return 闁绘鍩栭埀顑跨閸樼娀姊鹃崱顓犵濠㈡儼绮剧憴锔芥交閺傛寧绀€NULL
 */
QState* quantum_state_clone(QState* state);

/**
 * 闁瑰灚鎸稿畵鍐煂韫囨挾鎽嶉柣妯垮煐閳ь兛妞掓穱濠囧箒椤栥倗绀勯柣顫妺缁剛鎷崘顓犳Ц闁? * 
 * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐟扮樄闂? */
void quantum_state_print(QState* state);

/* 闁糕晝鍎ゅ﹢浼存煂韫囨挾鎽嶉柟鍨С缂嶆棃宕欓懞銉︽濠㈠湱澧楀Σ?*/
QState* create_qubit(void);
QState* create_qubit_state(double complex alpha, double complex beta);
QState* apply_hadamard(QState* qubit);
QState* apply_pauli_x(QState* qubit);
QState* apply_pauli_y(QState* qubit);
QState* apply_pauli_z(QState* qubit);
QState* apply_rotation_x(QState* qubit, double angle);
QState* apply_rotation_y(QState* qubit, double angle);
QState* apply_rotation_z(QState* qubit, double angle);
QState* apply_phase(QState* qubit, double angle);
QState* apply_t_gate(QState* qubit);

/* 婵炴潙顑夐崳铏圭磼閹惧浜紓浣规尰閻庮垱鎷?*/
typedef struct {
    int result;        // 婵炴潙顑夐崳铏圭磼閹惧浜?(0 闁?1)
    double probability; // 婵炴潙顑夐崳铏圭磼閹惧浜柣銊ュ椤┭囨偝?} MeasurementResult;

/* 婵炴潙顑夐崳娲礄閼恒儲娈?*/
MeasurementResult measure_qubit(QState* qubit);

#endif /* QENTL_QUANTUM_STATE_H */ 
