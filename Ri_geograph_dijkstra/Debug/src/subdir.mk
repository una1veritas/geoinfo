################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../src/geograph.cpp \
../src/geograph_dijkstra.cpp 

CPP_DEPS += \
./src/geograph.d \
./src/geograph_dijkstra.d 

OBJS += \
./src/geograph.o \
./src/geograph_dijkstra.o 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.cpp src/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	g++ -std=c++2a -O2 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


clean: clean-src

clean-src:
	-$(RM) ./src/geograph.d ./src/geograph.o ./src/geograph_dijkstra.d ./src/geograph_dijkstra.o

.PHONY: clean-src

