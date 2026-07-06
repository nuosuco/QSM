#include <stdio.h>
#include <string.h>
int main() {
  // simulate the flow: after CYCLE_STEPS: [{...}]
  // the data array is [{ ... }]
  // skip_to_semi_or_rbrace tracks brace depth
  // When it encounters ']' after '}', what is brace depth?
  // After '{' bd=1, '}' bd=0. consume.
  // Next token ']' — bd=0, not TOK_SEMI, not TOK_RBRACE (brace-balanced). So consume.
  // Then it sees quantum_class → consume → eats class!
  // BUG CONFIRMED.
  return 0;
}
