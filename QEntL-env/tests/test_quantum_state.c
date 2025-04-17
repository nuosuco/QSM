/*
 * 闂佹彃绻愰悺娆撴偐閼哥鍋撴担榧撲線宕稿Δ浣恒偞閻犲洦娲滈埢鍏兼償? * 闁活潿鍔嬬花顒侇殽瀹€鍐闂佹彃绻愰悺娆撴偐閼哥鍋撴担鐑樼ゲ闁稿繐鍟挎慨娑㈡嚄閻ｅ本鐣辨慨婵撶悼閳ユ﹢骞€? */

// 闂佹彃绻愰悺娆撳春閸濆嫭绀堢紓鍌涚墱閻?// QG-TEST-QSTATE-A1B1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <complex.h>
#include "../src/quantum_state.h"
#include "../src/quantum_gene.h"
#include "../src/quantum_entanglement.h"

// 婵炴潙顑堥惁顖炲礆濞戞绱﹂梺鎻掔箰閻℃瑩鎮╅懜纰樺亾?void test_create_quantum_state() {
    printf("Test: Creating quantum state...\n");
    
    QState* state = quantum_state_create("test_state_01");
    assert(state != NULL);
    assert(strcmp(state->name, "test_state_01") == 0);
    assert(state->type == QSTATE_BASIC);
    assert(state->property_count == 0);
    assert(state->entanglement_count == 0);
    
    printf("Passed: Quantum state creation test\n");
    quantum_state_destroy(state);
}

// 婵炴潙顑堥惁顖滄媼閸撗呮瀭闁告粌鐭侀獮蹇涘矗閺嵮呮剑闁?void test_state_properties() {
    printf("Test: Quantum state properties...\n");
    
    QState* state = quantum_state_create("test_state_02");
    
    // 閻犱礁澧介悿鍡欎沪閻愮补鍋?    int result1 = quantum_state_set_property(state, "color", "blue");
    int result2 = quantum_state_set_property(state, "energy", "high");
    
    assert(result1 == 1);
    assert(result2 == 1);
    assert(state->property_count == 2);
    
    // 闁兼儳鍢茶ぐ鍥╀沪閻愮补鍋?    const char* color = quantum_state_get_property(state, "color");
    const char* energy = quantum_state_get_property(state, "energy");
    
    assert(strcmp(color, "blue") == 0);
    assert(strcmp(energy, "high") == 0);
    
    // 婵炴潙顑堥惁顖炲即鐎涙ɑ鐓€閻忕偟鍋為埀?    result1 = quantum_state_set_property(state, "color", "red");
    assert(result1 == 1);
    color = quantum_state_get_property(state, "color");
    assert(strcmp(color, "red") == 0);
    assert(state->property_count == 2); // 闁轰椒鍗抽崳鐑樻償閺冨浂鍤夊☉鎾崇Т瑜?    
    // 婵炴潙顑堥惁顖炴嚔瀹勬澘绲垮☉鎾崇Т閻°劑宕烽妸褎鐣遍悘鐐靛仦閳?    const char* not_exist = quantum_state_get_property(state, "not_exist");
    assert(not_exist == NULL);
    
    printf("Passed: Quantum state properties test\n");
    quantum_state_destroy(state);
}

// 婵炴潙顑堥惁顖涙償閺冨倹鏆忛梺鎻掔箰閻℃瑩宕洪崫鍕
void test_apply_quantum_gene() {
    printf("Test: Applying quantum gene...\n");
    
    QState* state = quantum_state_create("test_state_03");
    QGene* gene = quantum_gene_create("test_gene_01", GENE_TYPE_OPERATION);
    
    // 閻犱礁澧介悿鍡涘春閸濆嫭绀堥悘鐐靛仦閳?    quantum_gene_add_property(gene, "operation", "superposition");
    quantum_gene_add_property(gene, "intensity", "0.8");
    
    // 婵犵鍋撴繛鑼额嚙閻斺偓闁?    quantum_gene_activate(gene, 0.7);
    
    // 閹煎瓨姊婚弫銈夊春閸濆嫭绀?
    int result = quantum_state_apply_gene(state, gene);
    assert(result == 1);
    assert(state->quantum_gene == gene);
    
    printf("Passed: Quantum gene application test\n");
    quantum_state_destroy(state);  // 闁告劕鎳橀崕瀛樻償閺傝法绉煎璺哄閹﹪宕洪崫鍕闁汇劌瀚伴崳鎾绩?}

// 婵炴潙顑堥惁顖炴煂韫囨挾鎽嶉柟顑跨劍缁佹挳鏌?void test_quantum_state_measure() {
    printf("Test: Quantum state measurement...\n");
    
    QState* state = quantum_state_create("test_state_04");
    
    // 閻犱礁澧介悿鍡曞悏闁告粌鐫曢崣澶婄泚妤?    state->alpha = 0.6 + 0.0 * I;
    state->beta = 0.8 + 0.0 * I;
    
    // 鐟滅増甯婄粩鎾礌?    double norm = sqrt(cabs(state->alpha) * cabs(state->alpha) + 
                       cabs(state->beta) * cabs(state->beta));
    state->alpha /= norm;
    state->beta /= norm;
    
    // 婵炴潙顑夐崳?    QState* measured = quantum_state_measure(state);
    assert(measured != NULL);
    assert(measured->type == QSTATE_MEASURED);
    
    // 婵炴潙顑夐崳娲触鎼达紕瀹夐悹鍥ュ劜濡插摜娑甸鑲╂毎闁?|0闁?闁?|1闁?    double alpha_magnitude = cabs(measured->alpha);
    double beta_magnitude = cabs(measured->beta);
    
    // 闁瑰灚鎸稿畵鍐圭€ｎ喖娅ょ紓浣规尰閻?    printf("Measurement result - alpha: %.4f, beta: %.4f\n", alpha_magnitude, beta_magnitude);
    
    // 婵炴潙顑夐崳娲触鎼达紕瀹夐柡鍕靛灣閳ユ鈧纰嶉埀?    assert((fabs(alpha_magnitude - 1.0) < 0.01 && fabs(beta_magnitude) < 0.01) || 
           (fabs(alpha_magnitude) < 0.01 && fabs(beta_magnitude - 1.0) < 0.01));
    
    printf("Passed: Quantum state measurement test\n");
    quantum_state_destroy(state);
    quantum_state_destroy(measured);
}

// 婵炴潙顑堥惁顖炴煂韫囨挾鎽嶉柟顑跨閸樼娀姊?void test_quantum_state_clone() {
    printf("Test: Quantum state cloning...\n");
    
    QState* original = quantum_state_create("original_state");
    
    // 閻犱礁澧介悿鍡涘储閻斿娼楅柟顑胯兌濞堟垹浠﹂悙绮瑰亾?    quantum_state_set_property(original, "color", "green");
    original->alpha = 0.3 + 0.1 * I;
    original->beta = 0.9 + 0.2 * I;
    
    // 闁稿繐顑夊▓?    QState* clone = quantum_state_clone(original);
    
    // 濡ょ姴鐭侀惁澶愬礂鐎ｎ喗鐣风紓浣规尰閻?    assert(clone != NULL);
    // 濞戞挸绉甸ˉ鍛村蓟閵夈儱寰斿ù锝嗘尭閹洜绮旂敮顔剧闁搞儳濮崇拹鐔衡偓鍦仧楠炲洭宕ｉ婵嗗幋闁哄牆顦版晶宥嗙▔瀹ュ懏鍊?
    assert(clone->name != NULL);
    assert(clone->type == original->type);
    
    // 濡ょ姴鐭侀惁澶屼沪閻愮补鍋?    const char* color = quantum_state_get_property(clone, "color");
    assert(strcmp(color, "green") == 0);
    
    // 濡ょ姴鐭侀惁澶愬箰椤栨氨鐣?
    assert(cabs(clone->alpha - original->alpha) < 0.01);
    assert(cabs(clone->beta - original->beta) < 0.01);
    
    printf("Passed: Quantum state cloning test\n");
    quantum_state_destroy(original);
    quantum_state_destroy(clone);
}

// 婵炴潙顑堥惁顖炴煂韫囨挾鎽嶇紒鍓уХ缁?void test_quantum_entanglement() {
    printf("Test: Quantum entanglement...\n");
    
    QState* state1 = quantum_state_create("entangled_state_1");
    QState* state2 = quantum_state_create("entangled_state_2");
    
    // 闁告帗绋戠紓鎾剁棯閻樼數鐐?
    QEntanglement* entanglement = quantum_entanglement_create("test_entanglement", state1, state2, 0.8);
    assert(entanglement != NULL);
    
    // 婵烇綀顕ф慨鐐电棯閻樼數鐐婇柛鎺撳婵悂骞€?    int result = quantum_state_add_entanglement(state1, entanglement);
    assert(result == 1);
    
    // 濡ょ姴鐭侀惁澶岀棯閻樼數鐐婃繛锝堫嚙婵偤骞嬮幇顒€顫犻柨娑樺缁茬偓绋夊鍡╂⒕闁哄被鍎遍崣鎸庢媴閹捐埖鐣辩紒鍓уХ缁卞爼寮导鏉戞闁挎稑鑻ú婊勭▔妤﹁法绠归柛娆樺灥閸忔﹢宕ｉ弽褍鏋€濞存粌楠搁悿鍕偝?    assert(state1->entanglements != NULL);
    
    // 濠碘€冲€归悘濉璶tanglement_count闁告瑯鍨禍鎺戭潰閿濆洠鈧ɑ鏅堕悙鎻掝潱闁挎稑鑻崹顖毼涢埀顒勫蓟閵夈倗鐟撻梻鍫涘灮濞堟垿寮堕垾鍙夘偨
    if (state1->entanglement_count > 0) {
        assert(state1->entanglements[state1->entanglement_count - 1] == entanglement);
    }
    
    printf("Passed: Quantum entanglement test\n");
    quantum_entanglement_destroy(entanglement);  // 濠㈣泛瀚幃濠勭棯閻樼數鐐婇柣銊ュ閺€銏犘?    quantum_state_destroy(state1);
    quantum_state_destroy(state2);
}

// 濞戞捁顕ч崵閬嶅极?int main() {
    printf("=== Quantum State Module Test ===\n");
    
    // 閺夆晜鍔橀、鎴﹀箥閳ь剟寮垫径瀣偞閻?    test_create_quantum_state();
    test_state_properties();
    test_apply_quantum_gene();
    test_quantum_state_measure();
    test_quantum_state_clone();
    test_quantum_entanglement();
    
    printf("=== All Tests Passed ===\n");
    return 0;
} 
