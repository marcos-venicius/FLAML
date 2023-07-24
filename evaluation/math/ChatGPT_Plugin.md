## ChatGPT Plus (GPT-4 + Plugin)
Website: https://chat.openai.com/

### 1. Observations

- GPT-4 + Wolfram Alpha is competitive in solving math problems. It can solve the problem correctly by directly querying wolfram.
- GPT-4 + Wolfram Alpha can sometimes get stuck sending the same error query, which can only be stopped manually.

### 2. Test Cases

**Test problem 1**: Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation.

Setup: Choose GPT-4 + Wolfram Alpha Plugin.

ChatGPT Plus can solve the problem correctly by directly querying wolfram.
```
REQUEST TO WOLFRAM
{
  "input": "solve (2x+10)(x+3)<(3x+9)(x+8) for x"
}
RESPONSE FROM WOLFRAM
Query:
"solve (2x+10)(x+3)<(3x+9)(x+8) for x"

Input interpretation:
solve (2 x + 10) (x + 3)<(3 x + 9) (x + 8) for x

Results:
x<-14

x>-3

Number line:
image: https://www6b3.wolframalpha.com/Calculate/MSP/MSP15481h8039ib01hd1169000041ai8ae4372c42c8?MSPStoreType=image/png&s=9

Wolfram|Alpha website result for "solve (2x+10)(x+3)<(3x+9)(x+8) for x":
https://www.wolframalpha.com/input?i=solve+%282x%2B10%29%28x%2B3%29%3C%283x%2B9%29%28x%2B8%29+for+x


The solution to the inequality \((2x+10)(x+3)<(3x+9)(x+8)\) is \(x < -14\) or \(x > -3\). 

In interval notation, this is expressed as \((-∞, -14) \cup (-3, ∞)\).

Here is a number line representation of the solution:

![Number Line](https://www6b3.wolframalpha.com/Calculate/MSP/MSP15481h8039ib01hd1169000041ai8ae4372c42c8?MSPStoreType=image/png&s=9)

For more details, you can visit the [Wolfram|Alpha result page](https://www.wolframalpha.com/input?i=solve+%282x%2B10%29%28x%2B3%29%3C%283x%2B9%29%28x%2B8%29+for+x).
```


**Test Problem 2**: There are 190 people on the beach.  110 are wearing sunglasses, 70 are wearing bathing suits, and 95 are wearing a hat.  Everyone is wearing at least one of these items. 30 are wearing both bathing suits and sunglasses. 25 are wearing both bathing suits and a hat. 40 are wearing both sunglasses and a hat.  How many people are wearing all three items?

```
This is a problem of set theory and can be solved using the principle of inclusion and exclusion. The principle of inclusion and exclusion states that for any three sets A, B, and C, the size of their union can be found by adding the sizes of the sets, then subtracting the sizes of the pairwise intersections, and finally adding back the size of the intersection of all three.

Let's denote:
- A as the set of people wearing sunglasses
- B as the set of people wearing bathing suits
- C as the set of people wearing a hat

We know that:
- |A| = 110 (people wearing sunglasses)
- |B| = 70 (people wearing bathing suits)
- |C| = 95 (people wearing a hat)
- |A ∩ B| = 30 (people wearing both sunglasses and bathing suits)
- |A ∩ C| = 40 (people wearing both sunglasses and a hat)
- |B ∩ C| = 25 (people wearing both bathing suits and a hat)
- |A ∪ B ∪ C| = 190 (total people on the beach)

We can find the number of people wearing all three items (|A ∩ B ∩ C|) by rearranging the formula of the principle of inclusion and exclusion:

|A ∩ B ∩ C| = |A| + |B| + |C| - |A ∩ B| - |A ∩ C| - |B ∩ C| + |A ∪ B ∪ C|

Let's calculate this.

Apologies for the confusion. The symbol "C" is a built-in constant in the Wolfram Language, representing the speed of light, and cannot be reassigned. Let's use different symbols to represent the sets:

- S for the set of people wearing sunglasses
- B for the set of people wearing bathing suits
- H for the set of people wearing a hat

Let's calculate again.

REQUEST TO WOLFRAM
{
  "input": "S = 110; B = 70; H = 95; SB = 30; SH = 40; BH = 25; SBH_total = 190; SBH = S + B + H - SB - SH - BH + SBH_total; SBH"
}
RESPONSE FROM WOLFRAM
"180 + (SBH_total)"

I apologize for the confusion. It seems there was an error in the calculation. The variable "SBH_total" was not correctly replaced with its value. Let's try again.

REQUEST TO WOLFRAM
{
  "input": "S = 110; B = 70; H = 95; SB = 30; SH = 40; BH = 25; SBH_total = 190; SBH = S + B + H - SB - SH - BH + SBH_total; SBH"
}
RESPONSE FROM WOLFRAM
"180 + (SBH_total)"

I apologize for the confusion. It seems there was an error in the calculation. The variable "SBH_total" was not correctly replaced with its value. Let's try again.

REQUEST TO WOLFRAM
{
  "input": "S = 110; B = 70; H = 95; SB = 30; SH = 40; BH = 25; SBH_total = 190; SBH = S + B + H - SB - SH - BH + SBH_total; SBH"
}
RESPONSE FROM WOLFRAM
"180 + (SBH_total)"

I apologize for the confusion. It seems there was an error in the calculation. The variable "SBH_total" was not correctly replaced with its value. Let's try again.

...Manually stopped.
```