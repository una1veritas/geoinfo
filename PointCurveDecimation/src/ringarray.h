/*
 * ringarray.h
 *
 *  Created on: 2026/03/18
 *      Author: sin
 */

#ifndef RINGARRAY_H_
#define RINGARRAY_H_

#include <vector>

template <typename T>
class RingArray {
    std::vector<T> array;
    size_t head = 0, tail = 0, count = 0;

public:
    RingArray(size_t capacity) : array(capacity) {}

	~RingArray() = default;

	bool is_empty() const {
		return count == 0; // head == tail
	}

    void push_back(T item) { // Enqueue
    	if (! count < array.size())	<--- いや、capacity では？
			resize(array.size()<<1); // Resize if full
    	array[tail] = item;
        tail = (tail + 1) % array.size();
        count++;
    }

    void push_front(T item) { // Enqueue
    	if (! count < array.size())
			resize(array.size()<<1); // Resize if full

    	head = (head + array.size() - 1) % array.size();
        array[head] = item;
        count++;
    }

    T pop_back() { // Enqueue
		if (count == 0)
			throw std::runtime_error("Buffer is empty");
		tail = (tail + array.size() - 1) % array.size();
		T item = array[tail];
		count--;
		return item;
    }

    T pop_front() { // Dequeue
		if (count == 0)
			throw std::runtime_error("Buffer is empty");
		T item = array[head];
		head = (head + 1) % array.size();
		count--;
		return item;
	}

    T& operator[](size_t i) { // Random access
        return array[(head + i) % array.size()];
    }

    void resize(size_t new_capacity) {
    	if (new_capacity <= array.size())
			return; // No shrinking
    	size_t old_capacity = array.size();
		array.resize(new_capacity);
		if (tail <= head) {
			for (size_t ix = 0; ix < tail; ++ix) {
				array[old_capacity + ix] = array[ix];
			}
			tail += old_capacity;
		}
		return;
	}
};


#endif /* RINGARRAY_H_ */
