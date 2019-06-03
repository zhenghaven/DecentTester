#pragma once

#include <cstdint>

#include <array>
#include <vector>
#include <string>

#include <DecentApi/Common/RuntimeException.h>

namespace Decent
{
	namespace Dht
	{
		namespace AccessCtrl
		{
			class EntityList;
			class FullPolicy;
		}
	}

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

		// ------- Functions for Decent Applications (enclaves):
		
		uint64_t GetSuccessorAddress(const std::array<uint8_t, sk_hashSizeByte>& key, void* cntPoolPtr, States& states);

		std::vector<uint8_t> AppReadData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key);

		void AppInsertData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const Dht::AccessCtrl::FullPolicy& accPolicy, const std::vector<uint8_t>& data);

		void AppUpdateData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data);

		void AppDeleteData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key);

		inline std::vector<uint8_t> AppReadData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
		{
			return AppReadData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key);
		}

		inline void AppInsertData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const Dht::AccessCtrl::FullPolicy& accPolicy, const std::vector<uint8_t>& data)
		{
			AppInsertData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key, accPolicy, data);
		}

		inline void AppUpdateData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const std::vector<uint8_t>& data)
		{
			AppUpdateData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key, data);
		}

		inline void AppDeleteData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
		{
			AppDeleteData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key);
		}

		// ------- Functions for Users (non-enclaves):

		uint64_t GetAttrListAddress(const std::string& listName, void* cntPoolPtr, States& states);

		void UserInsertAttrList(const uint64_t addr, void* cntPoolPtr, States& states, const std::string& listName, const Dht::AccessCtrl::EntityList& list);

		inline void UserInsertData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const Dht::AccessCtrl::FullPolicy& accPolicy, const std::vector<uint8_t>& data)
		{
			AppInsertData(addr, cntPoolPtr, states, key, accPolicy, data);
		}

		inline void UserInsertAttrList(void* cntPoolPtr, States& states, const std::string& listName, const Dht::AccessCtrl::EntityList& list)
		{
			UserInsertAttrList(GetAttrListAddress(listName, cntPoolPtr, states), cntPoolPtr, states, listName, list);
		}

		inline void UserInsertData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key, const Dht::AccessCtrl::FullPolicy& accPolicy, const std::vector<uint8_t>& data)
		{
			UserInsertData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key, accPolicy, data);
		}

		std::vector<uint8_t> UserReadData(const uint64_t addr, void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key);

		inline std::vector<uint8_t> UserReadData(void* cntPoolPtr, States& states, const std::array<uint8_t, sk_hashSizeByte>& key)
		{
			return UserReadData(GetSuccessorAddress(key, cntPoolPtr, states), cntPoolPtr, states, key);
		}
	}
}
