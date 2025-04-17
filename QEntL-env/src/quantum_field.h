/**
 * 闂佹彃绻愰悺娆撳捶閻戞◥渚€宕? * 
 * 閻庤鐭粻鐔哥閸濇エntL濞戞搩鍘惧▓鎴︽煂韫囨挾鎽嶉柛锕€鎼鐑藉礂閼稿灚鎯欏ù锝嗙矊閸ら亶寮懜顑藉亾? * 闂佹彃绻愰悺娆撳捶閻戞ɑ笑QEntL闁绘粠鍨伴。銊︾▔椤撶媭鍚€闁荤偛妫濋崳铏光偓娑欏姈閳ь兛绶氬▔锕傚触閸粎鐟㈤柛蹇旀构濮橈附绂嶉幒鏃€鐣卞Δ鍌涱焽妤犲洭骞庨崐鐔绘澖闁? */

#ifndef QENTL_QUANTUM_FIELD_H
#define QENTL_QUANTUM_FIELD_H

#include <stdint.h>
#include <stdlib.h>
#include "quantum_state.h"
#include "quantum_entanglement.h"

/**
 * 闂佹彃绻愰悺娆撳捶閾忕顫﹂柛銊ヮ儐閻忓洦绋? */
typedef enum {
    FIELD_TYPE_DETERMINISTIC,    // 缁绢収鍠栭悾楣冨箑瑜旈崳铏光偓娑欏姇濠р偓
    FIELD_TYPE_PROBABILISTIC,    // 婵帒鍊诲濂稿箑瑜旈崳铏光偓娑欏姇濠р偓
    FIELD_TYPE_EMOTIONAL,        // 闁诡垰鎳愰崡搴ㄥ垂鐎ｎ喖娅ら悗娑欏姇濠р偓
    FIELD_TYPE_COGNITIVE,        // 閻犱降鍊楅悡锟犲垂鐎ｎ喖娅ら悗娑欏姇濠р偓
    FIELD_TYPE_COMPOSITE,        // 濠㈣泛绉撮幃搴ㄥ垂鐎ｎ喖娅ら悗娑欏姇濠р偓
    FIELD_TYPE_DYNAMIC,          // 闁告柣鍔嶉埀顑跨窔閸ｈ櫣鈧稒鍔曞┃鈧?
    FIELD_TYPE_STRUCTURAL,       // 缂備焦鎸婚悗顖炲垂鐎ｎ喖娅ら悗娑欏姇濠р偓
    FIELD_TYPE_CUSTOM            // 闁煎浜滈悾鐐▕婢舵劕娅ら悗娑欏姇濠р偓
} QFieldType;

/**
 * 闁革妇鍎ら弲銉︽償閺冨倽顫﹂柛銊ヮ儐閻忓洦绋? */
typedef enum {
    EFFECT_AMPLIFICATION,        // 闁瑰壊鍨扮粻娆撳绩閹佷海
    EFFECT_ATTENUATION,          // 闁瑰壊鍨扮粻娆戞偘閺夊灝娅?
    EFFECT_PHASE_SHIFT,          // 闁烩晠鏅茬紞鍛村磻韫囨泤?    EFFECT_ENTANGLEMENT_BOOST,   // 缂佸墽濮风槐鑸垫櫠閻愭彃绻?
    EFFECT_COHERENCE_EXTEND,     // 闁烩晝顭堥崗閬嶅箑瑜嶅▎銏ゆ⒐?    EFFECT_DECOHERENCE,          // 闂侇偀鍋撻柣鈺冾焾閸忛亶寮崼婵堝畨
    EFFECT_STATE_COLLAPSE,       // 闁绘鍩栭埀顑跨濞兼梻绱?    EFFECT_CUSTOM                // 闁煎浜滈悾鐐▕婢跺娅忛幖?} FieldEffectType;

/**
 * 闂佹彃绻愰悺娆撳捶妤﹁法鐝堕柣锝呯灱鐞氼偊宕? */
typedef enum {
    BOUNDARY_OPEN,               // 鐎殿喒鍋撻柡鈧幑鎰彾闁?    BOUNDARY_REFLECTIVE,         // 闁告瑥绉撮惃鐘虫綇閸︻厽娅?
    BOUNDARY_PERIODIC,           // 闁告稏鍔嶅﹢锟犲箑瑜戠粩鐔兼偩?    BOUNDARY_ABSORBING,          // 闁告艾鎲￠弫瑙勬綇閸︻厽娅?
    BOUNDARY_CUSTOM              // 闁煎浜滈悾鐐▕婢跺海鐝堕柣?} FieldBoundaryType;

/**
 * 闁革箑鎼幃搴ㄧ嵁閸撲胶鎽滈柣? */
typedef enum {
    MERGE_ADD,                   // 闁烩晝顭堟慨?    MERGE_MULTIPLY,              // 闁烩晠鏅茬粻?    MERGE_MAX,                   // 闁告瑦鐗楀〒鑸靛緞瑜嶉埀?    MERGE_MIN,                   // 闁告瑦鐗楀〒鍓佷焊韫囨挴鍋?    MERGE_AVERAGE,               // 闁告瑦鐗曢柦鈺呭锤閸パ€鍋?    MERGE_CUSTOM                 // 闁煎浜滈悾鐐▕婢跺瞼鎽滈柣?} MergeStrategy;

/**
 * 闂佹彃绻愰悺娆撳捶缁℃墬
 * 闁哥儐鍨粩鎾冀閸ヮ亞妲曞☉鎾亾濞戞搩浜崳铏光偓娑欏姇濠р偓
 */
typedef struct {
    uint8_t id[32];              // 闂佹彃绻愰悺娆撳捶缁℃墬闁?56濞达絽绋勭槐?    char readable_id[65];        // 闁告瑯鍨甸浼村冀閻撳海纭€ID闁挎稑鐗嗗畷鍕礂椤擄紕绠婚柛鎺曟硾閻⊙呯箔閿旇儻顩柨?} QFieldID;

/**
 * 闁革箒娅ｉ崑锝夊锤閹邦厾鍨?
 * 閻炴稏鍔庨妵姘舵煂韫囨挾鎽嶉柛锕佹〃閼垫垿鎯冮崟顏嗩伇濞戞搩浜為崑? */
typedef struct {
    double x;                    // X闁秆勫姈閻?    double y;                    // Y闁秆勫姈閻?    double z;                    // Z闁秆勫姈閻?    double t;                    // 闁哄啫鐖煎Λ鍧楀锤閹邦厾鍨?
} FieldCoordinate;

/**
 * 闁革妇鍎ら弲銉︽償閺傚灝妫橀柡? * 闁硅绻楅崼顏堝捶閻戞ɑ娅忛幖瀛樻⒒濞堟垿鎮х憴鍕ㄥ亾? */
typedef struct {
    FieldEffectType type;        // 闁轰礁鐗嗙花鑼尵鐠囪尙鈧?    double strength;             // 闁轰礁鐗嗙花鎻掝嚕閸濆嫬顔婇柨?.0-1.0闁?    double range;                // 闁轰礁鐗嗙花鏌ユ嚑閸愩劍绾?
    double duration;             // 闁轰礁鐗嗙花鏌ュ箰娴ｈ櫣鏁鹃柡鍐ㄧ埣濡潡鏁嶉崼銏╂健闁?    void* custom_parameters;     // 闁煎浜滈悾鐐▕婢跺﹤妫橀柡浣稿簻缁辨瑩宕ｉ鐐╁亾婢舵稓绀?
} FieldEffectParameters;

/**
 * 闂佹彃绻愰悺娆撳捶妤﹀灝螡闁? * 閻炴稏鍔庨妵姘舵煂韫囨挾鎽嶉柛锕佹〃閼垫垿鎯冮崟顏嗩伇濞戞搩浜為崑锝夊矗婵犲倸寰撻柣妯垮煐閳? */
typedef struct {
    double x;                    // X闁秆勫姈閻?    double y;                    // Y闁秆勫姈閻?    double z;                    // Z闁秆勫姈閻?    double* position;            // 闂侇偅姘ㄩ弫銈嗘媴瀹ュ洨鏋傞柡浣瑰缁秹鏁嶇仦鐐殰闁归晲妞掗幑銏ゅ箛韫囨洘妯婇幖?    double intensity;            // 闁革箑鎼杈ㄦ償?    QState* state;               // 閻犲洢鍎抽崑锝夋儍閸曨垰娅ら悗娑欏姈閳?} QFieldNode;

/**
 * 闁革箓缂氭俊顓㈡倷閻у摜绀勯柛姘灥閹宕楅悡搴晣闁? */
typedef QFieldNode FieldNode;

/**
 * 闂佹彃绻愰悺娆撳捶妤﹁法鐝堕柣锝呮湰濞碱垱绂? */
typedef struct {
    FieldBoundaryType type;       // 閺夊牆婀遍弲顐ょ尵鐠囪尙鈧?    double x_min, x_max;          // X閺夌偟顥愮粩鐔兼偩?    double y_min, y_max;          // Y閺夌偟顥愮粩鐔兼偩?    double z_min, z_max;          // Z閺夌偟顥愮粩鐔兼偩?    void* custom_boundary_data;   // 闁煎浜滈悾鐐▕婢跺海鐝堕柣锝呮湰閺嗙喖骞?} FieldBoundaryCondition;

/**
 * 闂佹彃绻愰悺娆撳捶閻戞宸濋柛鏍ㄧ墳椤宕? */
typedef struct {
    char* rule_name;              // 閻熸瑥瀚崹顖炲触瀹ュ泦?    char* rule_description;       // 閻熸瑥瀚崹顖炲箵韫囨艾鐗?
    void* rule_parameters;        // 閻熸瑥瀚崹顖炲矗閸屾稒娈?
    void (*evolution_function)(struct QField*, double time_step); // 婵犳洘鏌ㄧ€垫煡宕欓懞銉︽闁圭娲幏?} FieldEvolutionRule;

/**
 * 闂佹彃绻愰悺娆撳捶閸濆嫬甯楅柡浣哄瀹? */
typedef struct {
    char* name;                   // 闂佹彃绻愰悺娆撳捶閸濆嫭鍊崇紒?    char* description;            // 闂佹彃绻愰悺娆撳捶閻戞ê浼庨弶?    char* creation_timestamp;     // 闁告帗绋戠紓鎾诲籍閸洘锛熼柟?    char* last_update_timestamp;  // 闁哄牃鍋撻柛姘濞插潡寮悧鍫燁槯闂傚倸鐡ㄩ崺?    char* creator_id;             // 闁告帗绋戠紓鎾绘嚀閸栴敧
    int version;                  // 闁绘鐗婂﹢浼村矗?    char* tags;                   // 闁哄秴娲ㄩ鐑芥晬閸儮鍋撳Δ鈧ぐ鍧楀礆閸℃稒顓鹃柨?} QFieldMetadata;

/**
 * 闂佹彃绻愰悺娆撳捶閾忓湱娉㈤柡? * 闁哄秶顭堢缓楣冨极閻楀牆绁︾紓浣规尰閻庮垶鏁嶅畝鍐︹偓鍐矆鏉炴壆顏卞☉鎿冧邯閸ｈ櫣鈧稒鍔曞┃鈧?
 */
typedef struct {
    char name[64];               // 闂佹彃绻愰悺娆撳捶閸濆嫭鍊崇紒?    QFieldType type;             // 闂佹彃绻愰悺娆撳捶閾忕顫﹂柛?    double strength;             // 闁革箑鎼杈ㄦ償?    double intensity;            // 闁革箑鎼杈ㄦ償?闁告艾濂旂粻鐔烘嫚?
    int dimension;               // 闁革箒娅ｅ▓鎴犵磼閺夋垵顔?
    QFieldNode* nodes;           // 闁革箒娅ｉ崑锝夊极閹殿喚鐭?
    int node_count;              // 闁革箒娅ｉ崑锝夊极娴兼潙娅?
    int max_nodes;               // 闁哄牃鍋撳鍫嗗棗螡闁绘劗鎳撻鎰版煂?    void* private_data;          // 缂佸鐒﹀﹢渚€寮悧鍫濈ウ
} QField;

/**
 * 闁革箓缂氶～鍥圭€ｎ剛娉㈤柡? */
typedef struct {
    QFieldID field_id;           // 闂佹彃绻愰悺娆撳捶缁℃墬
    FieldCoordinate* observation_points; // 閻熸瑥鍊圭粊鎾倷鐟欏嫭娈剁紓?    int point_count;                   // 閻熸瑥鍊圭粊鎾倷鐟欏嫭娈堕梺?    QState** observed_states;    // 閻熸瑥鍊圭粊鎾礆閹殿喗鐣遍梺鎻掔箰閻℃瑩骞€娴ｈ娈剁紓?    double* field_intensities;         // 闁革箑鎼杈ㄦ償閿旇姤娈剁紓?    char* observation_timestamp;       // 閻熸瑥鍊圭粊鎾籍閸洘锛熼柟?} FieldObservationResult;

/**
 * 闂佹彃绻愰悺娆撳捶閸濆嫬鍙℃繛鎴濐槹鑶╃€? */
typedef struct {
    QField* field_a;             // 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姇濠р偓
    QField* field_b;             // 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姇濠р偓
    double* interference_pattern;      // 妤犵偛寮剁粔鐟拔熼垾宕囩闁轰胶澧楀畵?    int pattern_resolution;            // 婵☆垪鈧磭纭€闁告帒妫滄ご鎼佹偝?    char* calculation_timestamp;       // 閻犱緤绱曢悾濠氬籍閸洘锛熼柟?} FieldInterferencePattern;

/* -------------------- 闂佹彃绻愰悺娆撳捶閸濆嫮鍞ㄩ柡鍫墯閹奸攱鎷呭鍐ㄦ瘣闁?-------------------- */

/**
 * 闁告帗绋戠紓鎾诲棘閹殿喗鐣遍梺鎻掔箰閻℃瑩宕风弧鎵?
 */
QFieldID create_quantum_field_id();

/**
 * 濞寸姴楠搁悺褏绮敂鑳洬闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柛锔剧槰D
 */
QFieldID create_field_id_from_string(const char* id_string);

/**
 * 婵絾妫佺欢婵囩▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕风弧鎵?
 */
int compare_field_ids(QFieldID id1, QFieldID id2);

/**
 * 闁告帗绋戠紓鎾寸▔閳ь剚绋夐鍛厐闁汇劌瀚伴崳铏光偓娑欏姇濠р偓
 * @param name 闁革箑鎼幃鏇犵矓? * @param type 闁革箒娅ｇ悮顐﹀垂? * @return 闁哄倹婢橀崹鍗烆嚈閾忚鐣遍梺鎻掔箰閻℃瑩宕烽悜妯虹樄闂? */
QField* quantum_field_create(const char* name, QFieldType type);

/**
 * 闂佸簱鍋撴慨锝勭窔閸ｈ櫣鈧稒鍔曞┃鈧鐐茬埣閸ｆ挳寮ㄩ幑鎰偒婵? * @param field 閻熸洑绶氶弨銏犘掓担鐑樼暠闂佹彃绻愰悺娆撳捶? */
void quantum_field_destroy(QField* field);

/**
 * 闁告碍鍨块崳铏光偓娑欏姇濠р偓婵烇綀顕ф慨鐐烘嚍閸屾粌浠?
 * @param field 闁烩晩鍠楅悥锝夋煂韫囨挾鎽嶉柛? * @param node 閻熸洑鐒﹂崸濠囧礉閻樺灚鐣遍柤鍝勫€婚崑? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_add_node(QField* field, QFieldNode* node);

/**
 * 闁兼儳鍢茶ぐ鍥箰閸パ呮毎濞达絽绉堕悿鍡涙儍閸曨偅绨氱€殿喖鎼€? * @param field 闂佹彃绻愰悺娆撳捶? * @param x x闁秆勫姈閻? * @param y y闁秆勫姈閻? * @param z z闁秆勫姈閻? * @return 閻犲洢鍎扮紞鍛磾椤旂偓鐣遍柛锕€鎼杈ㄦ償? */
double quantum_field_get_intensity_at(QField* field, double x, double y, double z);

/**
 * 閻忓繐妫濋崳铏光偓娑欏姉婵悂骞€娴ｈ鏉圭紓鍐惧枛濠€顏堝捶鏉炴媽鍘柣銊ュ鐎垫氨鈧鐭紞鍛磾? * @param field 闂佹彃绻愰悺娆撳捶? * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋? * @param x x闁秆勫姈閻? * @param y y闁秆勫姈閻? * @param z z闁秆勫姈閻? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_place_state(QField* field, QState* state, double x, double y, double z);

/**
 * 濞达絽娼￠崳铏光偓娑欏姇濠р偓鐟滄澘宕幖鐑芥煂韫囨挾鎽嶉柣妯垮煐閳? * @param field 闂佹彃绻愰悺娆撳捶? * @param state 闂佹彃绻愰悺娆撴偐閼哥鍋? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_influence_state(QField* field, QState* state);

/**
 * 濞达絽銇樼悮杈ㄧ▔椤忓牆娅ら悗娑欏姇濠р偓闁烩晠鏅茬花鐗堟媴濠婂懏鏆?
 * @param field1 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姇濠р偓
 * @param field2 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姇濠р偓
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_interact(QField* field1, QField* field2);

/**
 * 闁告瑯鍨甸～瀣礌閺嶎厼娅ら悗娑欏姇濠р偓
 * @param field 闂佹彃绻愰悺娆撳捶? * @param filename 閺夊牊鎸搁崵顓㈠棘閸ワ附顐介柛? * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€0闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛銉у仱閺佸﹦鎷犻婊呭灣
 */
int quantum_field_visualize(QField* field, const char* filename);

/* -------------------- 闂佹彃绻愰悺娆撳捶妤﹀灝螡闁绘劘顫夐幖閿嬫媴濠婂啫姣愰柡?-------------------- */

/**
 * 闁告碍鍨块崳铏光偓娑欏姇濠р偓婵烇綀顕ф慨鐐哄捶閾忕懓浠柤鍝勫€婚崑? */
void add_field_node(QField* field, FieldCoordinate coordinate, QState* state);

/**
 * 濞寸姴閰ｉ崳铏光偓娑欏姇濠р偓缂佸顭峰▍搴ㄥ捶閾忕懓浠柤鍝勫€婚崑? */
void remove_field_node(QField* field, FieldCoordinate coordinate);

/**
 * 闁革负鍔戦崳铏光偓娑欏姇濠р偓濞戞搩鍘介悡锟犲箥閹勭皻闁绘劗顢婃俊顓㈡倷? */
FieldNode* find_field_node(QField* field, FieldCoordinate coordinate);

/**
 * 闁兼儳鍢茶ぐ鍥箰閸パ呮毎闁秆勫姈閻栵綁鎳犻崘銊︾函闁告劕鎳愬▓鎴﹀捶閾忕懓浠柤鍝勫€婚崑? */
FieldNode** get_nodes_in_region(QField* field, 
                               double x_min, double x_max, 
                               double y_min, double y_max, 
                               double z_min, double z_max,
                               int* result_count);

/**
 * 闁哄洤鐡ㄩ弻濠囧捶閾忕懓浠柤鍝勫€婚崑锝夋儍閸曨垰娅ら悗娑欏姈閳? */
void update_node_state(QField* field, FieldCoordinate coordinate, QState* new_state);

/**
 * 閺夆晝鍋炵敮瀛樼▔閵堝嫰鍤嬮柛锕佹閸嬶綁鎳為崒婊冧化
 */
void connect_field_nodes(QField* field, FieldCoordinate coord1, FieldCoordinate coord2);

/* -------------------- 闂佹彃绻愰悺娆撳捶閻戞ɑ娅忛幖瀛樻煥閸ら亶寮?-------------------- */

/**
 * 闁革负鍔戦崳铏光偓娑欏姇濠р偓濞戞搩鍘肩花鏌ユ偨閵娿儲绨氶柡浣哥墕缁? */
void apply_field_effect(QField* field, FieldCoordinate center, FieldEffectParameters effect);

/**
 * 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柛锔惧劋鐏? */
void create_field_wave(QField* field, 
                      FieldCoordinate source, 
                      double amplitude, 
                      double frequency, 
                      double phase);

/**
 * 閹煎瓨姊婚弫銈夋煂韫囨挾鎽嶉柛锔惧劋椤亝鎯? */
void apply_field_gradient(QField* field, 
                         FieldCoordinate direction, 
                         double gradient_strength);

/**
 * 闁革负鍔嬬悮杈ㄧ▔椤忓牆娅ら悗娑欏姇濠р偓濞戞柨顑夊Λ鍧楀礆濞戞绱﹂柛锔芥そ濮ｂ偓闂? */
void create_field_tunnel(QField* field_a, 
                        FieldCoordinate point_a, 
                        QField* field_b, 
                        FieldCoordinate point_b,
                        double tunnel_strength);

/* -------------------- 闂佹彃绻愰悺娆撳捶閻戞宸濋柛鏍ㄧ墪閸ら亶寮?-------------------- */

/**
 * 婵烇綀顕ф慨鐐烘煂韫囨挾鎽嶉柛锔惧劋缁便劑宕犻弽顒夋綈闁? */
void add_evolution_rule(QField* field, FieldEvolutionRule rule);

/**
 * 缂佸顭峰▍搴ㄦ煂韫囨挾鎽嶉柛锔惧劋缁便劑宕犻弽顒夋綈闁? */
void remove_evolution_rule(QField* field, const char* rule_name);

/**
 * 婵犳洘鏌ㄧ€垫煡鏌岃箛鎾舵憤闁革箒妗ㄧ粩瀛樼▔椤忓懏顦ч梻鍌氱摠椤掔偤姊? */
void evolve_field(QField* field, double time_step);

/**
 * 婵☆垪鍓濈€氭瑩鏌岃箛鎾舵憤闁革妇鍎ょ槐銊╁礌閺嵮冪厒闁圭娲ら悾楣冨籍閸洘锛?
 */
void simulate_field_to_time(QField* field, double target_time, double time_step);

/**
 * 闂佹彃绉堕悿鍡涙煂韫囨挾鎽嶉柛锕€鎼崺宀勫礆濠靛棭娼楅柣妯垮煐閳? */
void reset_field(QField* field);

/* -------------------- 闂佹彃绻愰悺娆撳捶閸濆嫬鐎婚柡瀣姇閸ら亶寮?-------------------- */

/**
 * 閻犱緤绱曢悾濠氭煂韫囨挾鎽嶉柛锔惧劋閳ь剚妲掗崗姗€鏌? */
double calculate_field_energy(QField* field);

/**
 * 閻犱緤绱曢悾濠氭煂韫囨挾鎽嶉柛锕佹閸? */
double calculate_field_entropy(QField* field);

/**
 * 閻犱緤绱曢悾缁樼▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕烽搹瑙勭暠闁烩晠鏅查幎鈧幖? */
double calculate_field_similarity(QField* field_a, QField* field_b);

/**
 * 闁告帒妫欓悗浠嬫煂韫囨挾鎽嶉柛锕佹濞堟垿骞忛幘鏉戔叧闁绘顫夐埀? */
void* analyze_field_topology(QField* field);

/**
 * 婵☆偀鍋撴繛鏉戭儔閸ｈ櫣鈧稒鍔曞┃鈧☉鎿冨幘濞堟垵螣閳ュ磭纭€闁告粌鐬肩划銊╁几? */
void* detect_field_patterns(QField* field);

/* -------------------- 闂佹彃绻愰悺娆撳捶妤︽娼庢繛鏉戭儏閸ら亶寮?-------------------- */

/**
 * 閻熸瑥鍊圭粊鎾煂韫囨挾鎽嶉柛锕€鎼﹢顏堝箰閸パ呮毎闁? */
QState* observe_field_at_point(QField* field, FieldCoordinate point);

/**
 * 濠㈣埖姘ㄩ崑锝囨喆閸屾稓銈撮梺鎻掔箰閻℃瑩宕? */
FieldObservationResult* observe_field_at_points(QField* field, 
                                              FieldCoordinate* points, 
                                              int point_count);

/**
 * 閻犱緤绱曢悾缁樼▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕烽搹瑙勭暠妤犵偛寮剁粔鐟拔熼垾宕囩
 */
FieldInterferencePattern* calculate_field_interference(QField* field_a, 
                                                     QField* field_b);

/**
 * 闂佹彃绻愰悺娆撳捶閻戞ê顫岀憸鏉垮船閸╁本娼忛崘褏绉电紓浣规綑鐎? */
void* project_field_to_dimension(QField* field, int target_dimension);

/* -------------------- 闂佹彃绻愰悺娆撳捶閾忓湱鐪扮紓鍌滃У閹奸攱鎷呭鍐ㄦ瘣闁?-------------------- */

/**
 * 闁革负鍔戦崳铏光偓娑欏姇濠р偓濞戞搩鍘奸崹鍗烆嚈閾忓湱鐪扮紓鍌滃Т鐏忣垶宕? */
void create_entangled_region(QField* field, 
                            FieldCoordinate center, 
                            double radius, 
                            double entanglement_strength);

/**
 * 闁革负鍔嬬悮杈ㄧ▔椤忓牆娅ら悗娑欏姇濠р偓闂傚倹娼欓崹鍗烆嚈閾忓湱鐪扮紓鍌滃█閳ь剚宀告禍? */
EntanglementChannel* create_inter_field_entanglement(QField* field_a, 
                                                   FieldCoordinate point_a, 
                                                   QField* field_b, 
                                                   FieldCoordinate point_b);

/**
 * 缂佸墽濮风槐鑸电▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕烽搹瑙勭暠閻庣數鎳撶花鏌ュ礌閸濆嫮鍘?
 */
void entangle_field_regions(QField* field_a, 
                           FieldCoordinate center_a, 
                           double radius_a,
                           QField* field_b, 
                           FieldCoordinate center_b, 
                           double radius_b);

/**
 * 閻熸瑱缍佸▍搴ㄦ煂韫囨挾鎽嶉柛锕佹〃閼垫垿鎯冮崟顓犵湴缂? */
void disentangle_field_region(QField* field, FieldCoordinate center, double radius);

/* -------------------- 闂佹彃绻愰悺娆撳捶閸濆嫷鍤ら柛?閻庣數鍘ч崵顓㈠礄閼恒儲娈?-------------------- */

/**
 * 閻忓繐妫濋崳铏光偓娑欏姇濠р偓閹兼潙绻愰崹顏堝礌閺嶏箒绀嬪ù婊冪焷缁绘﹢宕氶懜鍨闁? */
void* serialize_quantum_field(QField* field, size_t* data_size);

/**
 * 濞寸姴绨肩花鈺傛交濞戞ê鐓戦柡浣哄瀹撲線宕ｅ鍛闁告帗顨呯€垫煡鏌岃箛鎾舵憤闁? */
QField* deserialize_quantum_field(void* data, size_t data_size);

/**
 * 閻忓繐妫濋崳铏光偓娑欏姇濠р偓閻庣數鍘ч崵顓熺▔缁℃摬ON闁哄秶鍘х槐? */
char* export_field_to_json(QField* field);

/**
 * 濞寸姴涓淪ON闁哄秶鍘х槐锛勨偓鐢靛帶閸欏棝鏌岃箛鎾舵憤闁? */
QField* import_field_from_json(const char* json_data);

/**
 * 閻忓繐妫濋崳铏光偓娑欏姇濠р偓闁绘鍩栭埀顑挎缁绘氨鈧稒锚閸╁矂寮崶锔筋偨
 */
int save_field_to_file(QField* field, const char* filename);

/**
 * 濞寸姴瀛╅弸鍐╃鐠哄搫顫ｉ弶鐐扮矙閸ｈ櫣鈧稒鍔曞┃鈧柣妯垮煐閳? */
QField* load_field_from_file(const char* filename);

/**
 * 闁告艾鐗嗛懟鐔哥▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕? * @param field1 缂佹鍏涚粩瀛樼▔椤忓牆娅ら悗娑欏姇濠р偓
 * @param field2 缂佹鍏涚花鈺傜▔椤忓牆娅ら悗娑欏姇濠р偓
 * @param strategy 闁告艾鐗嗛懟鐔虹驳閺嶎偅娈?
 * @return 闁告艾鐗嗛懟鐔煎触鎼达絾鐣遍柡鍌欏嵆閸ｈ櫣鈧稒鍔曞┃鈧?
 */
QField* quantum_field_merge(QField* field1, QField* field2, MergeStrategy strategy);

#endif /* QENTL_QUANTUM_FIELD_H */ 
