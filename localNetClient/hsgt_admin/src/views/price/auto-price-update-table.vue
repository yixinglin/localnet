<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.title" placeholder="Title" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.importance" placeholder="Imp" clearable style="width: 90px" class="filter-item">
        <el-option v-for="item in importanceOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="listQuery.type" placeholder="Type" clearable class="filter-item" style="width: 130px">
        <el-option v-for="item in calendarTypeOptions" :key="item.key" :label="item.display_name+'('+item.key+')'" :value="item.key" />
      </el-select>
      <el-select v-model="listQuery.sort" style="width: 140px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        Search
      </el-button>
      <el-button class="filter-item" style="margin-left: 20px;" type="primary" icon="el-icon-edit" @click="handleCreate">
        Add
      </el-button>
      <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">
        Export
      </el-button>
      <el-checkbox v-model="showProductName" class="filter-item" style="margin-left:15px;" @change="tableKey=tableKey+1">
        Produktname
      </el-checkbox>
    </div>

    <el-table
      v-if="list"
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @sort-change="sortChange"
    >
      <el-table-column type="index" label="#" align="center" width="50px"/>
      <el-table-column label="ID" prop="id" sortable="custom" align="center" width="130px" :class-name="getSortClass('id')">
        <template slot-scope="{row}">
          <a :href="`https://www.metro.de/marktplatz/product/` + row.productKey" target="_blank">
            {{ row.id }}
          </a>
        </template>
      </el-table-column>
      <el-table-column label="No. 1" align="center" width="100px">
        <template slot-scope="{row}">
          <span v-if="row.sellers.length">{{ row.sellers[0].shopName }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Rank" align="center" width="60px">
        <template slot-scope="{row}">
          <el-tag v-if="row.conf.strategyId==='UnitPriceStrategy'" type="info">单</el-tag>
          <el-tag v-else-if="row.conf.strategyId==='TotalPriceStrategy'" type="info">总</el-tag>
          <span class="link-type" @click="handleSellerData(row)"> {{ rank_(row) }} </span>
        </template>
      </el-table-column>
      <el-table-column label="U.Price" width="80px" align="center">
        <template slot-scope="{row}">
          <span style="color:blue;">{{ row.price.toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="L.Price" align="center" width="110px">
        <template slot-scope="{row}">
          <span v-if="row.conf.lowestPrice != null">
            <span v-if="row.sellers.length && !comparable(row)"> &#128543;</span>
            {{ row.conf.lowestPrice }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="Reduce" align="center" width="80px">
        <template slot-scope="{row}">
          <span>{{ reduced_(row).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Profit" align="center" width="80px">
        <template slot-scope="{row}">
          <span v-if="profit(row)>0" style="color:green;">+{{ profit(row).toFixed(2) }}</span>
          <span v-else style="color:red;">{{ profit(row).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Amount" align="center" width="80px">
        <template slot-scope="{row}">
          <span>{{ row.conf.offerAmount }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Note" align="center" width="120px">
        <template slot-scope="{row}">
          <span>{{ row.conf.offerNote }}</span>
        </template>
      </el-table-column>
      <el-table-column v-if="showProductName" label="Title" min-width="100px" width="300px">
        <template slot-scope="{row}">
          <span class="link-type" @click="handleUpdate(row)">{{ row.productName }}</span>
          <!-- <el-tag>{{ row.type | typeFilter }}</el-tag> -->
        </template>
      </el-table-column>
      <!-- <el-table-column label="Strategy" align="center" width="80px">
        <template slot-scope="{row}">
          <span> {{ row.conf.strategyId }} </span>
        </template>
      </el-table-column> -->
      <el-table-column label="Status" align="center" width="80px">
        <template slot-scope="{row}">
          <div v-if="row.conf.enabled">
            <span v-if="row.suggest.status===0" style="color:green;">可比价</span>
            <span v-else-if="row.suggest.status===1 || row.suggest.status===5" style="color:blue;">已满足</span>
            <span v-else-if="row.suggest.status===2" style="color:red;">亏损</span>
            <span v-else-if="row.suggest.status===3" style="color:orange;">风险</span>
            <span v-else-if="row.suggest.status===4" style="color:gray;">无效</span>
            <span v-else-if="row.suggest.status===6" style="color:purple;">调幅过大</span>
          </div>
        </template>
      </el-table-column>
      <!-- <el-table-column label="Comparable" align="center" width="80px">
        <template slot-scope="{row}">
          <el-tag v-if="!comparable(row)" type="warning"> NO </el-tag>
        </template>
      </el-table-column> -->
      <!--  <el-table-column label="Date" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.timestamp | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column> -->
      <!-- <el-table-column label="Author" width="110px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.author }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="Qty" width="80px" align="center">
        <template slot-scope="{row}">
          <span v-if="row.quantity > 0">{{ row.quantity }}</span>
          <span v-else style="color:red;">0</span>
        </template>
      </el-table-column>
      <!-- <el-table-column label="Imp" width="80px">
        <template slot-scope="{row}">
          <svg-icon v-for="n in + row.importance" :key="n" icon-class="star" class="meta-item__icon" />
        </template>
      </el-table-column> -->
      <!-- <el-table-column label="Readings" align="center" width="95">
        <template slot-scope="{row}">
          <span v-if="row.pageviews" class="link-type" @click="handleFetchPv(row.pageviews)">{{ row.pageviews }}</span>
          <span v-else>0</span>
        </template>
      </el-table-column> -->
      <!-- <el-table-column label="Status" class-name="status-col" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column> -->
      <el-table-column label="Enabled" align="center" width="80px">
        <template slot-scope="{row}">
          <el-tag v-if="row.conf.enabled"> On </el-tag>
          <el-tag v-else type="danger"> Off </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="{row,$index}">
          <el-button type="primary" size="mini" @click="handleEditPriceData(row)">
            Edit
          </el-button>
          <el-button size="mini" @click="handleConfigData(row)">
            Setting
          </el-button>
          <el-button size="mini" @click="handleSellerData(row)">
            Stats
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :visible.sync="dialogStatsVisible" title="Seller Statistics">
      <SellerStats
        title=""
        :lowestPrice="tempConfig.lowestPrice"
        :strategyId="tempConfig.strategyId"
        :selfName="selfName"
        :sellerData="tempSellers"
      />
    </el-dialog>

    <el-dialog :visible.sync="dialogConfigFormVisible" title="Configuration">
      <ConfigUpdateForm
        title="Configuration"
        :productId="tempConfig.productId"
        @closeDialog="dialogConfigFormVisible = false"
      />
    </el-dialog>

    <el-dialog :visible.sync="dialogEditPriceFormVisible" title="Edit Price">
      <EditPriceForm
        title="Edit Price"
        :productId="tempConfig.productId"
        @closeDialog="dialogEditPriceFormVisible = false"
      />
    </el-dialog>

  </div>
</template>

<script>
import { fetchList, fetchPv, createArticle, updateArticle } from '@/api/article'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
// import getters from '@/store/getters'
import { mapState } from 'vuex'
import SellerStats from './components/SellerStats'
import ConfigUpdateForm from './components/ConfigUpdateForm'
import EditPriceForm from './components/EditPriceForm.vue'

const calendarTypeOptions = [
  { key: 'CN', display_name: 'China' },
  { key: 'US', display_name: 'USA' },
  { key: 'JP', display_name: 'Japan' },
  { key: 'EU', display_name: 'Eurozone' }
]

// arr to obj, such as { CN : "China", US : "USA" }
const calendarTypeKeyValue = calendarTypeOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name
  return acc
}, {})

export default {
  name: 'ComplexTable',
  components: { Pagination, SellerStats, ConfigUpdateForm, EditPriceForm },
  directives: { waves },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'info',
        deleted: 'danger'
      }
      return statusMap[status]
    },
    typeFilter(type) {
      return calendarTypeKeyValue[type]
    }
  },
  data() {
    return {
      tableKey: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        importance: undefined,
        title: undefined,
        type: undefined,
        sort: '+id'
      },
      importanceOptions: [1, 2, 3],
      calendarTypeOptions,
      sortOptions: [{ label: 'ID Ascending', key: '+id' }, { label: 'ID Descending', key: '-id' }],
      statusOptions: ['published', 'draft', 'deleted'],
      showProductName: true,
      temp: {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        type: '',
        status: 'published'
      },
      tempSellers: [],
      tempConfig: [],
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogPvVisible: false,
      dialogStatsVisible: false,
      dialogConfigFormVisible: false,
      dialogEditPriceFormVisible: false,
      pvData: [],
      rules: {
        type: [{ required: true, message: 'type is required', trigger: 'change' }],
        timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
        title: [{ required: true, message: 'title is required', trigger: 'blur' }]
      },
      downloadLoading: false
    }
  },
  computed: {
    ...mapState({
      list: state => state.autoPriceUpdate.list,
      total: state => state.autoPriceUpdate.list.length,
      selfName: state => state.autoPriceUpdate.selfName
    })
  },
  created() {
    this.listLoading = true
    // this.$store.dispatch('autoPriceUpdate/generateList').then(resp => {
    //   this.listLoading = false
    // })
    this.initList()
  },
  methods: {
    profit(row) { return row.price - row.lowestPrice },
    rank_(row) {
      var nSellers = row.sellers.length
      var i = row.sellers.findIndex(s => this.selfName === s.shopName) + 1
      return `${i}/${nSellers}`
    },
    reduced_(row) {
      if (row.sellers.length === 0) {
        return 0
      }
      var seller = row.sellers[0]
      if (seller.shopName === this.selfName) {
        return 0
      } else {
        var self = row.sellers.filter(s => s.shopName === this.selfName)[0]
        var total = seller.price2 + seller.shippingGroup.unitCost
        return row.conf.strategyId === 'TotalPriceStrategy'
          ? total - self.shippingGroup.unitCost - self.price2 - 0.01
          : seller.price2 - self.price2 - 0.01
      }
    },
    comparable(row) {
      if (row.sellers.length === 1) {
        return true
      }
      var otherSellers = row.sellers.filter(s => s.shopName !== this.selfName)
      if (otherSellers.length > 0) {
        var seller = row.sellers[0]
        var total = seller.price2 + seller.shippingGroup.unitCost
        return total > row.lowestPrice
      } else {
        return false
      }
    },
    async initList() {
      var list_ = await this.$store.dispatch('autoPriceUpdate/generateList')
      await this.$store.dispatch('autoPriceUpdate/generateConfigurations').then(resp => {
        this.listLoading = false
      })
      for (let i = 0; i < list_.length; i++) {
        await this.$store.dispatch('autoPriceUpdate/updateSuggestById', list_[i].id)
          .catch(err => {
            console.error(err)
          })
        await this.$store.dispatch('autoPriceUpdate/updateSellersById', list_[i].id)
          .catch(err => {
            console.error(err)
          })
      }
    },
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total

        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: '操作Success',
        type: 'success'
      })
      row.status = status
    },
    sortChange(data) {
      const { prop, order } = data
      if (prop === 'id') {
        this.sortByID(order)
      }
    },
    sortByID(order) {
      if (order === 'ascending') {
        this.listQuery.sort = '+id'
      } else {
        this.listQuery.sort = '-id'
      }
      this.handleFilter()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        status: 'published',
        type: ''
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp.id = parseInt(Math.random() * 100) + 1024 // mock a id
          this.temp.author = 'vue-element-admin'
          createArticle(this.temp).then(() => {
            this.list.unshift(this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: 'Created Successfully',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.temp.timestamp = new Date(this.temp.timestamp)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          tempData.timestamp = +new Date(tempData.timestamp) // change Thu Nov 30 2017 16:41:05 GMT+0800 (CST) to 1512031311464
          updateArticle(tempData).then(() => {
            const index = this.list.findIndex(v => v.id === this.temp.id)
            this.list.splice(index, 1, this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: 'Success',
              message: 'Update Successfully',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleDelete(row, index) {
      this.$notify({
        title: 'Success',
        message: 'Delete Successfully',
        type: 'success',
        duration: 2000
      })
      this.list.splice(index, 1)
    },
    handleFetchPv(pv) {
      fetchPv(pv).then(response => {
        this.pvData = response.data.pvData
        this.dialogPvVisible = true
      })
    },
    handleDownload() {
      this.downloadLoading = true
      import('@/vendor/Export2Excel').then(excel => {
        const tHeader = ['timestamp', 'title', 'type', 'importance', 'status']
        const filterVal = ['timestamp', 'title', 'type', 'importance', 'status']
        const data = this.formatJson(filterVal)
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: 'table-list'
        })
        this.downloadLoading = false
      })
    },
    handleSellerData(row) {
      this.tempSellers = row.sellers
      this.tempConfig = row.conf
      this.dialogStatsVisible = !this.dialogStatsVisible
    },
    handleConfigData(row) {
      this.tempSellers = row.sellers
      this.tempConfig = row.conf
      this.dialogConfigFormVisible = !this.dialogConfigFormVisible
    },
    handleEditPriceData(row) {
      this.tempSellers = row.sellers
      this.tempConfig = row.conf
      this.dialogEditPriceFormVisible = !this.dialogEditPriceFormVisible
    },
    formatJson(filterVal) {
      return this.list.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        } else {
          return v[j]
        }
      }))
    },
    getSortClass: function(key) {
      const sort = this.listQuery.sort
      return sort === `+${key}` ? 'ascending' : 'descending'
    }
  }
}
</script>
