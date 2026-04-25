/*
 * ringarray.h
 *
 *  Created on: 2026/03/18
 *      Author: sin
 */

#ifndef RINGARRAY_H_
#define RINGARRAY_H_

#include <cstddef>
#include <stdexcept>

template <typename T>
class ringarray {
    T * array; 	// backbone array
    std::size_t _capacity, _head = 0, _tail = 0, _count = 0;

public:
    ringarray(const size_t & capa) : _capacity(capa), _head(0), _tail(0), _count(0) {
    	if (_capacity < 8)
    		_capacity = 8;
    	array = new T[_capacity];
    }

	~ringarray() {
		delete [] array;
		_capacity = 0;
	}

	size_t size() const {
		return _count;
	}

	size_t capacity() const {
		return _capacity;
	}

	bool is_empty() const {
		return _count == 0; // head == tail
	}

	// enqueue
    void push_back(T item) {
    	if ( ! (_count < _capacity) ) {
    		resize(_capacity << 1); // Resize if full
    	}
    	array[_tail++] = item;
    	_tail %= _capacity;
        _count++;
    }

    void push_front(T item) {
    	if (! (_count < _capacity) )
			resize(_capacity<<1); // Resize if full
    	_head = (_head + _capacity - 1) % _capacity;
        array[_head] = item;
        _count++;
    }

    T pop_back() { // dequeue
//		if (count == 0)
//			throw std::runtime_error("Buffer is empty");
		_tail = (_tail + _capacity - 1) % _capacity;
		T item = array[_tail];
		_count--;
		return item;
    }

    T pop_front() { // dequeue
//		if (count == 0)
//			throw std::runtime_error("Buffer is empty");
		T item = array[_head];
		_head = (_head + 1) % _capacity;
		_count--;
		return item;
	}

    // Random access to ix-th element from the head position
    T& operator[](const size_t & ix) {
    	if (ix > _count)
    		throw std::out_of_range("Index is out of ringarray bounds");
        return array[(_head + ix) % _capacity];
    }

    void resize(size_t new_capa) {
    	if (new_capa <= _capacity)
			return; // No shrinking
    	T * new_array = new T[new_capa];
    	size_t ix;
		for (ix = 0; ix < _count; ++ix) {
			new_array[ix] = array[(_head + ix) % _capacity];
		}
		delete [] array;
		array = new_array;
		_capacity = new_capa;
		_head = 0;
		_tail = ix;
		return;
	}
};


#endif /* RINGARRAY_H_ */
