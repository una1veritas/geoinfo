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

#include <bit>
#include <vector>
#include <algorithm>

template <typename T>
class ringarray {
    std::vector<T> array; 	// backbone array
    std::size_t _capacity, _head = 0, _tail = 0, _count = 0;

public:
    ringarray(const size_t & capa = 16) : _capacity(capa), _head(0), _tail(0), _count(0) {
    	_capacity = std::bit_ceil(std::max(_capacity, size_t(16) ));
    	array.resize(_capacity);
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

	void clear(void) {
		_capacity = 0, _head = 0, _tail = 0, _count = 0;
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
    // takes signed integer as index
    T& operator[](const long & ix) {
    	if (ix < 0) {
    		long iy = _count + ix;
			if (iy < 0)
				throw std::out_of_range("Index is out of ringarray bounds");
			return array[(_head + iy) % _capacity];
    	} else {
			if (ix < _count)
				return array[(_head + ix) % _capacity];
			throw std::out_of_range("Index is out of ringarray bounds");
    	}
    }

    const T& operator[](const long & ix) const {
    	if (ix < 0) {
    		long iy = _count + ix;
			if (iy < 0)
				throw std::out_of_range("Index is out of ringarray bounds");
			return array[(_head + iy) % _capacity];
    	} else {
			if (ix < _count)
				return array[(_head + ix) % _capacity];
			throw std::out_of_range("Index is out of ringarray bounds");
    	}
    }

    void resize(const size_t & new_capa) {
    	if (new_capa <= _capacity)
			return; // No shrinking
    	size_t new_size = std::bit_ceil( new_capa + 1 );
    	if (new_size <= std::max(_capacity, new_capa) ) {
    		throw std::out_of_range("Index is out of ringarray bounds");
    	}
    	std::vector<T> new_array(new_size);
    	size_t ix;
		for (ix = 0; ix < _count; ++ix) {
			new_array[_head + ix] = array[(_head + ix) % _capacity];
		}
		array = std::move(new_array);
		_capacity = new_size;
		_tail = _head + ix;
		return;
	}
};


#endif /* RINGARRAY_H_ */
