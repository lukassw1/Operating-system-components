#include "monitor.h"
#include <iostream>
#include <string>
#include <queue>
#include <deque>
#include <chrono>
#include <thread>
#include <pthread.h>
using namespace std;
int CONST_SLEEP = 500;

Semaphore global(1), semProdEven(0), semProdOdd(0), semConsEven(0), semConsOdd(0);
unsigned int numOfProdEvenWaiting = 0, numOfProdOddWaiting = 0, numOfConsEvenWaiting = 0, numOfConsOddWaiting = 0;

void printDeque(deque<int> d){
   cout << "buffor: ";
   for(auto &i: d){
      cout << i << ", ";
   }
   cout << "\n";
}

class Buffer{
   private:
   deque<int> data;
   public:
   int firstOutNumber(){return data.front();}
   int countOdd(){
      int ret = 0;
      for(auto &i: data){if(i%2==1) ret++;}
      return ret;
   }
   int countEven(){
      int ret = 0;
      for(auto &i: data){if(i%2==0) ret++;}
      return ret;
   }
   void put(int element){data.push_back(element); printDeque(data);}
   int get(){int ret = data.front(); data.pop_front(); return ret;}

   bool canPutEven(){if (countEven()<10) return true; return false;}
   bool canPutOdd(){if (countEven()>countOdd()) return true; return false;}
   bool canConsEven(){if (countEven()+countOdd()>=3 && !data.empty() && firstOutNumber() % 2 == 0) return true; return false;}
   bool canConsOdd(){if (countEven()+countOdd()>=7 && !data.empty() && firstOutNumber() % 2 == 1) return true; return false;}

   void putEven(int element){
      global.p();
      if (!canPutEven()){
         numOfProdEvenWaiting++;
         global.v();
         semProdEven.p();
         numOfProdEvenWaiting--;
      }

      put(element);

      if(numOfProdOddWaiting > 0 && canPutOdd()){semProdOdd.v();}
      else if(numOfConsEvenWaiting > 0 && canConsEven()){semConsEven.v();}
      else if(numOfConsOddWaiting > 0 && canConsOdd()){semConsOdd.v();}
      else {global.v();}
   }

   void putOdd(int element){
      global.p();
      if (!canPutOdd()){
         numOfProdOddWaiting++;
         global.v();
         semProdOdd.p();
         numOfProdOddWaiting--;
      }

      put(element);

      if(numOfProdEvenWaiting > 0 && canPutEven()){semProdEven.v();}
      else if(numOfConsEvenWaiting > 0 && canConsEven()){semConsEven.v();}
      else if(numOfConsOddWaiting > 0 && canConsOdd()){semConsOdd.v();}
      else {global.v();}
   }

   void getEven(){
      global.p();
      if (!canConsEven()){
         numOfConsEvenWaiting++;
         global.v();
         semConsEven.p();
         numOfConsEvenWaiting--;
      }

      int rem = get();
      cout << "Even consumerremoved: " << rem << "\n";

      if(numOfProdEvenWaiting > 0 && canPutEven()){semProdEven.v();}
      else if(numOfProdOddWaiting > 0 && canPutOdd()){semProdOdd.v();}
      else if(numOfConsOddWaiting > 0 && canConsOdd()){semConsOdd.v();}
      else {global.v();}
   }

   void getOdd(){
      global.p();
      if (!canConsOdd()){
         numOfConsOddWaiting++;
         global.v();
         semConsOdd.p();
         numOfConsOddWaiting--;
      }

      int rem = get();
      cout << "Odd consumer removed: " << rem << "\n";

      if(numOfProdEvenWaiting > 0 && canPutEven()){semProdEven.v();}
      else if(numOfProdOddWaiting > 0 && canPutOdd()){semProdOdd.v();}
      else if(numOfConsEvenWaiting > 0 && canConsEven()){semConsEven.v();}
      else {global.v();}
   }
};

Buffer buffer;

void evenProducer(){
   while(true){
      int element = rand()%25 * 2;
      buffer.putEven(element);
      this_thread::sleep_for(chrono::milliseconds(CONST_SLEEP+rand()%1000));
   }
}

void oddProducer(){
   while(true){
      int element = rand()%25 * 2 + 1;
      buffer.putOdd(element);
      this_thread::sleep_for(chrono::milliseconds(CONST_SLEEP+rand()%1000));
   }
}

void evenCons(){
   while(true){
      buffer.getEven();
      this_thread::sleep_for(chrono::milliseconds(CONST_SLEEP+rand()%1000));
   }
}

void oddCons(){
   while(true){
      buffer.getOdd();
      this_thread::sleep_for(chrono::milliseconds(CONST_SLEEP+rand()%1000));
   }
}
                                    // 1. grupa testów
void test1000(){evenProducer();}    // 1000 -> 9/10
void test0100(){oddProducer();}     // 0100 -> pusto
void test0010(){evenCons();}        // 0010 -> pusto
void test0001(){oddCons();}         // 0010 -> pusto
                                    // 2.grupa testów
void test1100(){                    // 1100 -> max 19/20
   thread th1(evenProducer);
   thread th2(oddProducer);
   th1.join();
   th2.join();
}
void test0011(){                    // 0011 -> pusto
   thread th1(evenCons);
   thread th2(oddCons);
   th1.join();
   th2.join();
}
void test1010(){                    // 1010 -> prawidłowe działanie na liczbach parzystych
   thread th1(evenProducer);
   thread th2(evenCons);
   th1.join();
   th2.join();
}
void test0101(){                    // 0101 -> pusto
   thread th1(oddProducer);
   thread th2(oddCons);
   th1.join();
   th2.join();
}

void test1111(){                    // 1111 -> prawidłowe działanie
   thread th1(evenProducer);
   thread th2(oddProducer);
   thread th3(evenCons);
   thread th4(oddCons);
   th1.join();
   th2.join();
   th3.join();
   th4.join();
}

int main() {                        
   //test1000();
   //test0100();
   //test0010();
   //test0001();

   //test1100();
   //test0011();
   //test1010();
   //test0101();

   test1111();
   return 0;
}