#include <iostream>
#include <iomanip>
#include <cmath>
#include <limits>


int main(void)
{
  long double d1 = -330.8374555644710;
  long double d2 = -330.8374552433434;
  long double d3 = -330.8374546013530;
  long double d4 = -330.8374542804908;
  long double t1 = -330.8380230265347;
  long double t2 = -330.8380225750420;
  long double t4 = -330.8380216723222;
  long double t5 = -330.8380212210931;

  //double d1 = -330.83745556;
  //double d2 = -330.83745524;
  //double d3 = -330.83745460;
  //double d4 = -330.83745428;
  std::cout << -1 * d1 + 2 * d2 -2 * d3 + d4 << std::endl;
  std::cout << -1*t1 + 2 * t2 - 2*t4 + t5 << std::endl;
  return 0; 
}
