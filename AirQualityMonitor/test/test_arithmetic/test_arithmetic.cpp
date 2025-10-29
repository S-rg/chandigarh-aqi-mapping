#include <Arduino.h>
#include <unity.h>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    int product = 0;
    for (int i = 0; i < a; i++) {
        product += b;
    }
    return product;
}

// Test Cases
void test_addition() {
    TEST_ASSERT_EQUAL(32, add(25, 7));
}

void test_negative_addition() {
    TEST_ASSERT_EQUAL(-5, add(-2, -3));
}

void test_multiplication() {
    TEST_ASSERT_EQUAL(15, multiply(3, 5));
}

// Setup runs the tests
void setup() {
    delay(2000);
    UNITY_BEGIN();

    RUN_TEST(test_addition);
    RUN_TEST(test_negative_addition);
    RUN_TEST(test_multiplication);

    UNITY_END();
}

// Loop is uned for test
void loop() {
}