/**
 * QEntL闂佹彃绻愰悺娆撳春閸濆嫭绀堝璺虹摠閺嬪啯绂?- 缂佺姭鍋撻柛鏍ㄧ墱婢?
 * 
 * @闁哄倸娲ｅ▎? quantum_gene.h
 * @闁硅绻楅崼? 閻庤鐭粻鐔兼煂韫囨挾鎽嶉柛鈺佹惈濞叉粓鎯冮崟顐ゅ敤闁哄牜鍓涚划銊╁几閸曨偅瀚查柟鍨С缂嶆棃宕欓懞銉︽
 * @闁绘鐗婂﹢? 1.0
 */

#ifndef QENTL_QUANTUM_GENE_H
#define QENTL_QUANTUM_GENE_H

#include <stdlib.h>
#include <stdint.h>

/* 闁告挸绉撮幃婊勭珶閻楀牊顫?*/
struct QState;
typedef struct QState QState;
struct QEntanglement;
typedef struct QEntanglement QEntanglement;

/**
 * 闂佹彃绻愰悺娆撳春閸濆嫭绀堢紒顐ヮ嚙閻庣兘寮稿顐㈩洭
 */
typedef enum {
    GENE_TYPE_CONTROL,      // 闁硅矇鍐ㄧ厬闁糕晛鎼ú?
    GENE_TYPE_OPERATION,    // 闁瑰灝绉崇紞鏃堝春閸濆嫭绀?
    GENE_TYPE_STRUCTURE,    // 缂備焦鎸婚悗顖炲春閸濆嫭绀?
    GENE_TYPE_ENTANGLEMENT, // 缂佸墽濮风槐鍫曞春閸濆嫭绀?
    GENE_TYPE_MEASUREMENT,  // 婵炴潙顑夐崳娲春閸濆嫭绀?
    GENE_TYPE_CUSTOM        // 闁煎浜滈悾鐐▕婢跺﹦鍞ㄩ柛?
} QGeneType;

/**
 * 闂佹彃绻愰悺娆撳春閸濆嫭绀堥悘鐐靛仦閳?
 */
typedef struct {
    char* name;            // 閻忕偟鍋為埀顑啯鍊崇紒?
    char* value;           // 閻忕偟鍋為埀顑啠鍋?
} QGeneProperty;

/**
 * 闂佹彃绻愰悺娆撳春閸濆嫭绀堥悶娑栧姀閹活亪宕ｉ崒娑欐
 */
typedef struct {
    int is_active;         // 闁哄嫷鍨伴幆浣该洪弰蹇曗攬
    double strength;       // 閻炴稏鍔忛幓顏勵嚕閸濆嫬顔婇柨?.0-1.0闁?
    double stability;      // 缂佸鍟块悾楣冨箑瑜濈槐?.0-1.0闁?
    double mutation_rate;  // 缂佹劒绀佽ぐ澶愭偝?
} QGeneExpression;

/**
 * 闂佹彃绻愰悺娆撳春閸濆嫭绀堢紓浣规尰閻?
 */
typedef struct QGene {
    char* id;                  // 闁糕晛鎼ú娣欴
    QGeneType type;            // 闁糕晛鎼ú婊呯尵鐠囪尙鈧?
    QGeneProperty* properties; // 闁糕晛鎼ú婊呬沪閻愮补鍋撹閺嗙喓绱?
    size_t property_count;     // 閻忕偟鍋為埀顑嫭娈堕梺?
    QGeneExpression expression; // 閻炴稏鍔忛幓顏堝矗閸屾稒娈?
} QGene;

/**
 * 闂佹彃绻愰悺娆撳春閸濆嫭绀堥幖?
 */
typedef struct {
    QGene** genes;         // 闁糕晛鎼ú婊堝极閹殿喚鐭?
    size_t gene_count;     // 闁糕晛鎼ú婊堝极娴兼潙娅?
} QGeneBank;

/* -------------------- 闁糕晛鎼ú婊呯不閿涘嫭鍊為柛鎴ｅГ閺?-------------------- */

/**
 * 闁告帗绋戠紓鎾诲棘閹殿喗鐣遍梺鎻掔箰閻℃瑩宕洪崫鍕
 * 
 * @param id 闁糕晛鎼ú娣欴
 * @param type 闁糕晛鎼ú婊呯尵鐠囪尙鈧?
 * @return 闁糕晛鎼ú婊堝箰閸ヮ剚瀚涢柨娑樿嫰閵囨垹鎷归妷銊х闁搞儲鎱稶LL
 */
QGene* quantum_gene_create(const char* id, QGeneType type);

/**
 * 闂佸簱鍋撴慨锝勭窔閸ｈ櫣鈧稒鍔曢悢鈧柛?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 */
void quantum_gene_destroy(QGene* gene);

/**
 * 婵烇綀顕ф慨鐐哄箣閺嶃劍绾柡鍌涙緲閻斺偓闁搞儳濮撮惈姗€骞€?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @param name 閻忕偟鍋為埀顑啯鍊?
 * @param value 閻忕偟鍋為埀顑啠鍋?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_gene_add_property(QGene* gene, const char* name, const char* value);

/**
 * 闁兼儳鍢茶ぐ鍥春閸濆嫭绀堥悘鐐靛仦閳?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @param name 閻忕偟鍋為埀顑啯鍊?
 * @return 閻忕偟鍋為埀顑啠鍋撶涵椋庣濞戞挸绉撮悺銊╁捶閵娿劎绠查柛銉︽叿ULL
 */
const char* quantum_gene_get_property(QGene* gene, const char* name);

/**
 * 婵犵鍋撴繛鑼额嚙閻斺偓闁?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @param strength 閻炴稏鍔忛幓顏勵嚕閸濆嫬顔?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_gene_activate(QGene* gene, double strength);

/**
 * 闁稿绮庨弫銈夊春閸濆嫭绀?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_gene_deactivate(QGene* gene);

/**
 * 闁稿繐顑夊▓鏇㈠春閸濆嫭绀?
 * 
 * @param gene 婵犙勫姇閻斺偓闁?
 * @return 闁稿繐顑夊▓鏇㈡儍閸曨偆鍞ㄩ柛銉у缁辨繃寰勬潏顐バ曢弶鈺傛煥濞叉湝ULL
 */
QGene* quantum_gene_clone(QGene* gene);

/**
 * 闁糕晛鎼ú婊呯玻娴ｇ缍?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_gene_mutate(QGene* gene);

/**
 * 闁瑰灚鎸稿畵鍐春閸濆嫭绀堝ǎ鍥ｅ墲娴?
 * 
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 */
void quantum_gene_print(QGene* gene);

/* -------------------- 闁糕晛鎼ú婊勬償閹鹃鍚€闁荤偛妫楅崵閬嶅极?-------------------- */

/**
 * 闁告帗绋戠紓鎾诲春閸濆嫭绀堥幖?
 * 
 * @return 闁糕晛鎼ú婊勬償閹炬潙鐦归梺钘夌墳缁辨繃寰勬潏顐バ曢弶鈺傛煥濞叉湝ULL
 */
QGeneBank* quantum_gene_bank_create();

/**
 * 闂佸簱鍋撴慨锝勭閻斺偓闁搞儳濮寸花?
 * 
 * @param bank 闁糕晛鎼ú婊勬償閹炬潙鐦归梺?
 */
void quantum_gene_bank_destroy(QGeneBank* bank);

/**
 * 闁告碍鍨甸悢鈧柛銉уТ缁ㄥ崬菐鐠囨彃顫ｉ柛鈺佹惈濞?
 * 
 * @param bank 闁糕晛鎼ú婊勬償閹炬潙鐦归梺?
 * @param gene 闁糕晛鎼ú婊堝箰閸ヮ剚瀚?
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_gene_bank_add_gene(QGeneBank* bank, QGene* gene);

/**
 * 濞寸姴楠搁悢鈧柛銉уТ缁ㄩ亶寮婚妷锕€顥濋柛鈺佹惈濞?
 * 
 * @param bank 闁糕晛鎼ú婊勬償閹炬潙鐦归梺?
 * @param id 闁糕晛鎼ú娣欴
 * @return 闁糕晛鎼ú婊堝箰閸ヮ剚瀚涢柨娑樺缁楀鈧稒锚濠€顏呮交閺傛寧绀€NULL
 */
QGene* quantum_gene_bank_find_gene(QGeneBank* bank, const char* id);

/**
 * 濞寸姴楠搁悢鈧柛銉уТ缁ㄨ京绮旀繝姘彑闁糕晛鎼ú?
 * 
 * @param bank 闁糕晛鎼ú婊勬償閹炬潙鐦归梺?
 * @param id 闁糕晛鎼ú娣欴
 * @return 闁瑰瓨鍔曟慨娑欐交閺傛寧绀€1闁挎稑鑻妵鎴犳嫻閵夈劎绠查柛?
 */
int quantum_gene_bank_remove_gene(QGeneBank* bank, const char* id);

#endif /* QENTL_QUANTUM_GENE_H */ 
