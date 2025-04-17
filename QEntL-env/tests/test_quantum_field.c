/*
 * 闂佹彃绻愰悺娆撳捶閻戞◥渚€宕稿Δ浣恒偞閻犲洦娲滈埢鍏兼償? * 闁活潿鍔嬬花顒侇殽瀹€鍐闂佹彃绻愰悺娆撳捶閾忚绁查柛蹇撳暱婵盯鎳楅悾灞剧暠婵繐绲块垾姗€骞€? */

// 闂佹彃绻愰悺娆撳春閸濆嫭绀堢紓鍌涚墱閻?// QG-TEST-QFIELD-A1B1

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <complex.h>
#include "../src/quantum_field.h"
#include "../src/quantum_state.h"

// 婵炴潙顑堥惁顖炲礆濞戞绱﹂梺鎻掔箰閻℃瑩宕?void test_create_quantum_field() {
    printf("婵炴潙顑堥惁顖炴晬濮橆剙鐏＄€点倖妞介崳铏光偓娑欏姇濠р偓...\n");
    
    QField* field = quantum_field_create("test_field_01", FIELD_TYPE_COGNITIVE);
    assert(field != NULL);
    assert(strcmp(field->name, "test_field_01") == 0);
    assert(field->type == FIELD_TYPE_COGNITIVE);
    assert(field->strength == 1.0); // 濮掓稒顭堥璇差嚕閸濆嫬顔?
    assert(field->node_count == 0);
    
    printf("闂侇偅淇虹换鍐晬濮橆剙鐏＄€点倖妞介崳铏光偓娑欏姇濠р偓婵炴潙顑堥惁鐥媙");
    quantum_field_destroy(field);
}

// 婵炴潙顑堥惁顖毲庣拠鎻掝潱闁革箓缂氭俊顓㈡倷?void test_add_field_nodes() {
    printf("婵炴潙顑堥惁顖炴晬濮橆厼娼戦柛鏃傚Т濠р偓闁煎搫鍊婚崑?..\n");
    
    QField* field = quantum_field_create("test_field_02", FIELD_TYPE_DYNAMIC);
    
    // 婵烇綀顕ф慨鐐哄捶妤﹀灝螡闁?    QFieldNode node1;
    node1.x = 1.0;
    node1.y = 2.0;
    node1.z = 3.0;
    node1.intensity = 0.8;
    node1.state = NULL;
    node1.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    QFieldNode node2;
    node2.x = 4.0;
    node2.y = 5.0;
    node2.z = 6.0;
    node2.intensity = 0.6;
    node2.state = NULL;
    node2.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    quantum_field_add_node(field, &node1);
    quantum_field_add_node(field, &node2);
    
    // 濡ょ姴鐭侀惁澶愭嚍閸屾粌浠柡浣峰嵆閸?    assert(field->node_count == 2);
    
    // 濡ょ姴鐭侀惁澶愭嚍閸屾粌浠柛褎鍔栭悥?    assert(field->nodes[0].x == 1.0);
    assert(field->nodes[0].y == 2.0);
    assert(field->nodes[0].z == 3.0);
    assert(field->nodes[0].intensity == 0.8);
    
    assert(field->nodes[1].x == 4.0);
    assert(field->nodes[1].y == 5.0);
    assert(field->nodes[1].z == 6.0);
    assert(field->nodes[1].intensity == 0.6);
    
    printf("闂侇偅淇虹换鍐晬濮橆厼娼戦柛鏃傚Т濠р偓闁煎搫鍊婚崑锝吤圭€ｎ厾妲竆n");
    quantum_field_destroy(field);
}

// 婵炴潙顑堥惁顖炲捶閾忚鐣辩€殿喖鎼€瑰磭鎷嬮敍鍕毈
void test_field_intensity() {
    printf("婵炴潙顑堥惁顖炴晬濮橆剚绨氱€殿喖鎼€瑰磭鎷嬮敍鍕毈...\n");
    
    QField* field = quantum_field_create("test_field_03", FIELD_TYPE_COGNITIVE);
    
    // 婵烇綀顕ф慨鐐寸▔閳ь剚绋夐鍕皻闁煎搫鍊婚崑锝夋晬瀹€鈧弫銈嗙鎼达絾绾柟鎭掑劜缁佸鎷?    QFieldNode node;
    node.x = 0.0;
    node.y = 0.0;
    node.z = 0.0;
    node.intensity = 1.0;
    node.state = NULL;
    node.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    quantum_field_add_node(field, &node);
    
    // 閻犱緤绱曢悾濠氬捶閾忕懓浠€殿喖鎼€?    double intensity = quantum_field_get_intensity_at(field, 0.0, 0.0, 0.0);
    
    // 濡ょ姴鐭侀惁澶婎嚕閸濆嫬顔?- 闁烩晛鐡ㄧ敮瀛樻媴瀹ュ洨鏋傞幖瀛樻椤曟岸寮?.0
    assert(fabs(intensity - 1.0) < 0.01);
    
    // 閻犱緤绱曢悾濠氭閻愬弶绨氶柣鎰扳偓娑氱Т缂傚喚鍠栧杈ㄦ償閿旇偐绀勯柟缁樺笒閳ь剛銆嬬槐?    double intensity2 = quantum_field_get_intensity_at(field, 0.5, 0.5, 0.5);
    
    // 鐎殿喖鎼€硅櫕鎯旈弮鍥跺殙闁?闁?濞戞柨顑夊Λ?    assert(intensity2 > 0.0 && intensity2 < 1.0);
    
    printf("闂侇偅淇虹换鍐晬濮橆剚绨氱€殿喖鎼€瑰磭鎷嬮敍鍕毈婵炴潙顑堥惁鐥媙");
    quantum_field_destroy(field);
}

// 婵炴潙顑堥惁顖炲捶閸濆嫷鍤犻梺鎻掔箰閻℃瑩鎮╅懜纰樺亾娴ｇ儤鐣辩憸鏉垮船閹?void test_field_influence_on_state() {
    printf("婵炴潙顑堥惁顖炴晬濮橆剚绨氶悗闈涚秺閸ｈ櫣鈧稒鍔楁慨鎼佸箑娴ｇ儤鐣辩憸鏉垮船閹?..\n");
    
    // 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柛?    QField* field = quantum_field_create("test_field_04", FIELD_TYPE_EMOTIONAL);
    field->strength = 0.9;
    
    // 婵烇綀顕ф慨鐐哄捶妤﹀灝螡闁?    QFieldNode node;
    node.x = 0.0;
    node.y = 0.0;
    node.z = 0.0;
    node.intensity = 1.0;
    node.state = NULL;
    node.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    quantum_field_add_node(field, &node);
    
    // 闁告帗绋戠紓鎾绘煂韫囨挾鎽嶉柣妯垮煐閳?    QState* state = quantum_state_create("test_state_in_field");
    quantum_state_set_property(state, "state_type", "emotional");
    
    // 閻犱礁澧介悿鍡涘礆濠靛棭娼楅梺鎻掔箰閻℃瑩骞愰姘辩暯
    state->alpha = 0.3 + 0.0 * I;
    state->beta = 0.7 + 0.0 * I;
    
    // 闁革负鍔屽┃鈧☉鎿冨幗閸у﹪宕濋悩闈浶﹂柟顑挎缂嶅懐绱?    quantum_field_place_state(field, state, 0.0, 0.0, 0.0);
    
    // 閹煎瓨姊婚弫銈夊捶閾忚鐣辩憸鏉垮船閹?    quantum_field_influence_state(field, state);
    
    // 濡ょ姴鐭侀惁澶愭偐閼哥鍋撴担绋跨秮闁?    // 闁汇垹褰夌花顒勫捶閾忚鐣辩憸鏉垮船閹肩兘鏁嶅畝鈧慨鎼佸箑娴ｅ摜瀹夐柛娆愬灩閺佹捇宕ｅΟ鍝勵嚙
    double alpha_magnitude = cabs(state->alpha);
    double beta_magnitude = cabs(state->beta);
    
    // 闁瑰灚鎸稿畵鍐偓鍦仱濡绢垶宕愰梻缈犵鞍濞撴俺鍎婚惃鐔烘嫚?    printf("鐟滄澘宕幖鐑藉触鎼达絾鐣盿lpha闁瑰壊鍨扮粻? %.4f (濡澘瀚﹢?> 0.3)\n", alpha_magnitude);
    printf("鐟滄澘宕幖鐑藉触鎼达絾鐣眀eta闁瑰壊鍨扮粻? %.4f (濡澘瀚﹢鈩冪▔瀹ュ嫮顏遍悗?< 0.7)\n", beta_magnitude);
    
    // 濡ょ姴鐭侀惁澶愬箰椤栨氨鐣介柛娆惷€?    assert(alpha_magnitude != 0.3); // 闁瑰壊鍨扮粻娆愭償閺冨浂鍤夐柛娆愬灩閺佹捇宕ｅΟ鍝勵嚙
    
    printf("闂侇偅淇虹换鍐晬濮橆剚绨氶悗闈涚秺閸ｈ櫣鈧稒鍔楁慨鎼佸箑娴ｇ儤鐣辩憸鏉垮船閹煎嘲霉鐎ｎ厾妲竆n");
    quantum_field_destroy(field);
    quantum_state_destroy(state);
}

// 婵炴潙顑堥惁顖炲捶閾忚鐣遍柧璇茬Т閹?void test_field_merge() {
    printf("婵炴潙顑堥惁顖炴晬濮橆剚绨氶柧璇茬Т閹?..\n");
    
    // 闁告帗绋戠紓鎾寸▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕?    QField* field1 = quantum_field_create("test_field_merge_1", FIELD_TYPE_PROBABILISTIC);
    QField* field2 = quantum_field_create("test_field_merge_2", FIELD_TYPE_PROBABILISTIC);
    
    // 濞戞挸鎼┃鈧?婵烇綀顕ф慨鐐烘嚍閸屾粌浠?
    QFieldNode node1;
    node1.x = 0.0;
    node1.y = 0.0;
    node1.z = 0.0;
    node1.intensity = 0.8;
    node1.state = NULL;
    node1.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    quantum_field_add_node(field1, &node1);
    
    // 濞戞挸鎼┃鈧?婵烇綀顕ф慨鐐烘嚍閸屾粌浠?
    QFieldNode node2;
    node2.x = 1.0;
    node2.y = 1.0;
    node2.z = 1.0;
    node2.intensity = 0.6;
    node2.state = NULL;
    node2.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    quantum_field_add_node(field2, &node2);
    
    // 闁捐绉撮幃搴ㄥ捶?    QField* merged = quantum_field_merge(field1, field2, MERGE_ADD);
    
    // 濡ょ姴鐭侀惁澶愭懚瀹ュ懏鍊ょ紓浣规尰閻?    assert(merged != NULL);
    assert(strncmp(merged->name, "test_field_merge_1_test_field_merge_2", 63) == 0);
    assert(merged->type == FIELD_TYPE_PROBABILISTIC);
    assert(merged->node_count == 2);
    
    // 濡ょ姴鐭侀惁澶愬捶妤﹀灝螡闁绘劘顫夊Σ鎼佸触閿旂瓔鍔€缁绢収鍠氶幋鐑藉箥?    assert(merged->nodes[0].x == 0.0);
    assert(merged->nodes[0].y == 0.0);
    assert(merged->nodes[0].z == 0.0);
    assert(merged->nodes[0].intensity == 0.8);
    
    assert(merged->nodes[1].x == 1.0);
    assert(merged->nodes[1].y == 1.0);
    assert(merged->nodes[1].z == 1.0);
    assert(merged->nodes[1].intensity == 0.6);
    
    printf("闂侇偅淇虹换鍐晬濮橆剚绨氶柧璇茬Т閹骸霉鐎ｎ厾妲竆n");
    quantum_field_destroy(field1);
    quantum_field_destroy(field2);
    quantum_field_destroy(merged);
}

// 婵炴潙顑堥惁顖炲捶閾忚鐣遍柣鈺呮櫜缁ㄧ増鎷呭鍛殢
void test_field_interaction() {
    printf("婵炴潙顑堥惁顖炴晬濮橆剚绨氶柣銊ュ濞村绂嶉幒宥囩▕闁?..\n");
    
    // 闁告帗绋戠紓鎾寸▔閵堝嫰鍤嬮梺鎻掔箰閻℃瑩宕?    QField* field1 = quantum_field_create("interaction_field_1", FIELD_TYPE_COGNITIVE);
    QField* field2 = quantum_field_create("interaction_field_2", FIELD_TYPE_COGNITIVE);
    
    // 婵烇綀顕ф慨鐐哄捶妤﹀灝螡闁?    QFieldNode node1;
    node1.x = 0.0;
    node1.y = 0.0;
    node1.z = 0.0;
    node1.intensity = 0.8;
    node1.state = NULL;
    node1.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    QFieldNode node2;
    node2.x = 0.5;
    node2.y = 0.5;
    node2.z = 0.5;
    node2.intensity = 0.7;
    node2.state = NULL;
    node2.position = NULL;  // 濞戞挸鐡ㄥ鍌毭圭€ｎ厾妲搁柨娑樿嫰閻ゅ嫰姊介崨顓犲畨闁圭娲ら幃婊堝嫉婢跺娅忛柛鎰噹閻?    
    quantum_field_add_node(field1, &node1);
    quantum_field_add_node(field2, &node2);
    
    // 婵炴潙顑堥惁顖炲捶閾忚鐣遍柣鈺呮櫜缁ㄧ増鎷呭鍛殢
    int interaction_result = quantum_field_interact(field1, field2);
    assert(interaction_result == 0); // 闁瑰瓨鍔曟慨娑欑閵堝嫮闉?
    
    // 婵☆偀鍋撻柡灞诲劙濮橈附绂嶉幒鎴炲€甸柣銊ュ濠р偓鐎殿喖鎼ぐ澶愬礌?    assert(field1->strength != 1.0);
    assert(field2->strength != 1.0);
    
    printf("闂侇偅淇虹换鍐晬濮橆剚绨氶柣銊ュ濞村绂嶉幒宥囩▕闁活潿鍔嶇粊瀵告嫚閺勭€?);
    quantum_field_destroy(field1);
    quantum_field_destroy(field2);
}

// 濞戞捁顕ч崵閬嶅极?int main() {
    printf("=== 闂佹彃绻愰悺娆撳捶閻戞◥渚€宕稿Δ浣恒偞閻?===\n");
    
    // 閺夆晜鍔橀、鎴﹀箥閳ь剟寮垫径瀣偞閻?    test_create_quantum_field();
    test_add_field_nodes();
    test_field_intensity();
    test_field_influence_on_state();
    test_field_merge();
    test_field_interaction();
    
    printf("=== 闁圭鍋撻柡鍫濐槹缁佸鎷犻弴鈶╁亾濮樺磭绠?===\n");
    return 0;
} 
