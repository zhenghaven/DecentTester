#pragma once

#include <cstdint>

#include <array>
#include <vector>
#include <string>

#include <DecentApi/Common/RuntimeException.h>

namespace Decent
{
	namespace DhtClient
	{
		class States;

		class DataNonExist : public RuntimeException
		{
		public:
			DataNonExist() :
				RuntimeException("Request data does not exist in the DHT store.")
			{}
		};

		class PermissionDenied : public RuntimeException
		{
		public:
			PermissionDenied() :
				RuntimeException("Request has been denied because of the permission.")
			{}
		};

		/**
		 * \brief	The size of hash in Bytes.
		 */
		constexpr size_t sk_hashSizeByte = 32;
		
		uint64_t GetSuccessorAddress(const std::array<uint8_t, sk_hashSizeByte>& key, void* cntPoolPtr, States& states);

		std::vector<uint8_t> AppReadData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key);

		void AppInsertData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& meta, const std::vector<uint8_t>& data);

		void AppUpdateData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data);

		void AppDeleteData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key);

		inline std::vector<uint8_t> AppReadData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
		{
			return AppReadData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key);
		}

		inline void AppInsertData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& meta, const std::vector<uint8_t>& data)
		{
			AppInsertData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key, meta, data);
		}

		inline void AppUpdateData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data)
		{
			AppUpdateData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key, data);
		}

		inline void AppDeleteData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
		{
			AppDeleteData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key);
		}
	}
}
