#pragma once

#include <cstdint>

#include <array>
#include <vector>
#include <string>

namespace Decent
{
	namespace Dht
	{
		/**
		 * \brief	The size of hash in Bytes.
		 */
		constexpr size_t sk_hashSizeByte = 32;
		
		uint64_t GetSuccessorAddress(const std::array<uint8_t, sk_hashSizeByte>& key, void* cntPoolPtr);

		void GetData(const uint64_t addr, void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, std::vector<uint8_t>& outData);

		void SetData(const uint64_t addr, void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data);

		void GetData(const uint64_t addr, void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, std::string& outData);

		void SetData(const uint64_t addr, void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, const std::string& data);

		void DelData(const uint64_t addr, void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key);

		inline void GetData(void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, std::vector<uint8_t>& outData)
		{
			GetData(GetSuccessorAddress(key, cntPoolPtr), cntPoolPtr, key, outData);
		}

		inline void SetData(void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data)
		{
			SetData(GetSuccessorAddress(key, cntPoolPtr), cntPoolPtr, key, data);
		}

		inline void GetData(void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, std::string& outData)
		{
			GetData(GetSuccessorAddress(key, cntPoolPtr), cntPoolPtr, key, outData);
		}

		inline void SetData(void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key, const std::string& data)
		{
			SetData(GetSuccessorAddress(key, cntPoolPtr), cntPoolPtr, key, data);
		}

		inline void DelData(void* cntPoolPtr, const std::array<uint8_t, sk_hashSizeByte>& key)
		{
			DelData(GetSuccessorAddress(key, cntPoolPtr), cntPoolPtr, key);
		}
	}
}
