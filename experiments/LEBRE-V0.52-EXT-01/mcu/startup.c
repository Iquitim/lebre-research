/* startup.c — minimal Cortex-M4F startup: vector table, .data/.bss initialisation, FPU enable, main(). */
#include <stdint.h>
extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss, _estack;
int main(void);
void Reset_Handler(void) {
    uint32_t *s = &_sidata, *d = &_sdata;
    while (d < &_edata) *d++ = *s++;
    for (d = &_sbss; d < &_ebss;) *d++ = 0;
    *(volatile uint32_t *)0xE000ED88 |= (0xFu << 20);         /* CPACR: full access to CP10/CP11 (FPU) */
    __asm volatile("dsb\n isb");
    main();
    for (;;) {}
}
void Default_Handler(void) { for (;;) {} }
__attribute__((section(".isr_vector"))) const void *vectors[16] = {
    &_estack, Reset_Handler, Default_Handler, Default_Handler, Default_Handler, Default_Handler, Default_Handler, 0, 0, 0, 0,
    Default_Handler, Default_Handler, 0, Default_Handler, Default_Handler};
