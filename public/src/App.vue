<template>
  <div id="app">
    <modal
      :id="modalId"
      header-flavor="Info"
      :header="true"
      top-offset="50px"
      :footer="true"
    >
      <template v-slot:header>
        <section-title>Sources</section-title>
      </template>
      <template v-slot:body>
        <list class="source-list">
          <list-item v-for="source in selectedItem.sources" :key="source">
            <web-link :href="source">{{source}}</web-link>
          </list-item>
        </list>
      </template>
      <template v-slot:footer>
        <n-button flavor="Light" @click="closeModal">Close</n-button>
      </template>
    </modal>
    <vue-me :parent-instance="this"></vue-me>
    <nav class="navbar">
      <page-title flavor="Dark">Protest Data Visualization</page-title>
      <web-link flavor="Dark" href="#" @click="showWhatThis">What's this?</web-link>
    </nav>
    <div 
      :tabindex="showFilters ? '' : -1" class="filters"
      :class="{'filters--closed': !showFilters}">
      <div class="filters__title">
        <section-title>Filters</section-title>
        <button-group class="filters__buttongroup">
          <n-button small flavor="Light"  @click="showFilters = false">Close Filters</n-button>
          <n-button small flavor="Primary" @click="retrieveItems" >Apply Filters</n-button>
          <n-button small flavor="Warning" @click="clearFilters" >Clear Filters</n-button>
        </button-group>
      </div>
      <vue-input 
        input-type="text"
        label="Search by City"
        name="citysearch"
        placeholder="Partial matches included"
        v-model="filters.city__icontains">
      </vue-input>
      <vue-input 
        input-type="text"
        label="Search by Location"
        name="locationsearch"
        placeholder="Partial matches included"
        v-model="filters.location__icontains">
      </vue-input>
      <vue-input 
        input-type="text"
        label="Search by County"
        name="countsearch"
        placeholder="Partial matches included"
        v-model="filters.county__icontains">
      </vue-input>
      <date-picker
        label="Date On or After"
        name="dateOnOrAfter"
        :end="filters.date__lte"
        v-model="filters.date__gte"
      ></date-picker>
      <date-picker
        label="Date On or Before"
        name="dateOnOrBefore"
        :start="filters.date__gte"
        v-model="filters.date__lte"
      ></date-picker>
      <n-label for="stsearch">Search by Available State</n-label>
      <select-me
        name="stsearch"
        :multi-select="true"
        v-model="filters.state__in"
        :options="stateOptions">
      </select-me>
      <n-label for="eventtypesearch">Search by Event Type</n-label>
      <select-me
        name="eventtypesearch"
        :multi-select="true"
        v-model="filters.event_type__in"
        :options="eventTypeOptions">
      </select-me>
      <vue-input 
        input-type="text"
        label="Search by Actor"
        name="actorsearch"
        placeholder="Partial matches included"
        v-model="filters.actor__icontains">
      </vue-input>
      <vue-input 
        input-type="text"
        label="Search by Claim"
        name="claimsearch"
        placeholder="Partial matches included"
        v-model="filters.claim__icontains">
      </vue-input>
      <number-range
        v-for="(numberrange, index) in numberRanges"
        :key="`numberrange-${index}`"
        :max="fetchMinMax(numberrange.filter, 'max')"
        :min="fetchMinMax(numberrange.filter, 'min')"
        :steps="[1]"
        :label="numberrange.label"
        :name="numberrange.filter"
        @change="changeMinMax(numberrange.filter, $event)"
        v-model="filters[numberrange.filter]"
      >
      </number-range>
      <button-group class="filters__buttongroup">
        <n-button small flavor="Light"  @click="showFilters = false">Close Filters</n-button>
        <n-button small flavor="Primary" @click="retrieveItems" >Apply Filters</n-button>
        <n-button small flavor="Warning" @click="clearFilters" >Clear Filters</n-button>
      </button-group>
    </div>
    <div
      :tabindex="showTableConfiguration ? '' : -1"
      class="tableconfiguration"
      :class="{'tableconfiguration--closed': !showTableConfiguration}">
      <div class="tableconfiguration__title">
        <section-title>Configure Table</section-title>
        <n-button block flavor="Light"  @click="showTableConfiguration = false">Close Table Configuration</n-button>
        <list>
          <list-item v-for="header in headers" :key="`select-${header.value}`">
            <checkbox
              @input="handleCheckboxClick(header)"
              :value="shownHeaders.map(h => h.value).indexOf(header.value) != -1"
              label-flavor="Dark"
              :label="header.text"
            >
            </checkbox>
          </list-item>
        </list>
      </div>
    </div>
    <div class="maincontent">
      <div class="container">
        <div class="grapharea">
          <div class="grapharea--empty" v-if="graphs.length == 0">
            <section-title>Start adding graphs using the "Add Graph" button.</section-title>
          </div>
        </div>
        <div class="buttoncontainer">
          <n-button flavor="Primary" @click="showFilters = true">Filters</n-button>
          <n-button flavor="Warning">Add Graph</n-button>
          <n-button flavor="Info" @click="showTableConfiguration = true">Configure Table</n-button>
          <div class="pagination-controls">
            <paginator 
              :margin-pages="1"
              :page-range="3"
              @select="handleSelect"
              :page-count="pagination.numPages"
              :current-page="pagination.currentPage">
            </paginator>
            <text-content class="pagination-info">Showing {{pagination.start}} to {{pagination.end}} of {{pagination.total}}</text-content>
          </div>
        </div>
        <vue-raw-table class="table">
          <template v-slot:header>
            <table-row>
              <table-header flavor="Dark" v-for="header in shownHeaders" :key="header.value">
                <web-link href="#" class="table__header" @click="setOrder(header.value)">{{header.text}}</web-link>
                <table-carat
                class="tablecarat"
                  flavor="Dark"
                  :class="order_by == header.value ? '': order_by == `-${header.value}` ? 'table-open-carat' : 'table-not-shown'"
                >

                </table-carat>
              </table-header>
              <table-header flavor="Dark">
                &nbsp;
              </table-header>
            </table-row>
          </template>
          <template v-slot:body>
            <table-row v-if="inFlight">
              <table-cell :colspan="shownHeaders.length + 1" class="table--loading">
                <span class="sr-only">Loading</span>
                <i class="fa fa-spinner fa-pulse fa-3x"></i>
              </table-cell>
            </table-row>
            <table-row v-else v-for="item in items" :key="item.id">
              <table-cell v-for="header in shownHeaders" :key="`${item.id}-${header.value}`">
                <text-content>{{formatValue(item[header.value])}}</text-content>
              </table-cell>
              <table-cell>
                <n-button flavor="Info" @click="openModal(item)">View Sources</n-button>
              </table-cell>
            </table-row>
          </template>
        </vue-raw-table>
      </div>
    </div>
    <footer class="footer">
      <text-content>Web Application 2020 &copy; Pedro Del Moral Lopez</text-content>
      <text-content>Data belongs to <web-link href="https://sites.google.com/view/crowdcountingconsortium/home">Crowd Counting Consortium</web-link></text-content>
    </footer>
  </div>
</template>

<script>
import {PageTitle, WebLink, TextContent, SectionTitle, NLabel} from "@IntusFacultas/typography"
import {VueMe} from "@IntusFacultas/vue-me";
import {NButton, ButtonGroup} from "@IntusFacultas/button";
import VueRawTable from "@IntusFacultas/raw-table";
import VueInput from "@IntusFacultas/input"
import {TableRow, TableCell, TableHeader, TableCarat} from "@IntusFacultas/table"
import {List, ListItem} from "@IntusFacultas/list"
import Paginator from "@IntusFacultas/paginator";
import axios from "axios";
import "font-awesome/css/font-awesome.min.css";
import Checkbox from "@IntusFacultas/checkbox";
import SelectMe from "@IntusFacultas/select-me";
import DatePicker from "@IntusFacultas/date-picker"
import NumberRange from "@IntusFacultas/number-range";
import Modal from "@IntusFacultas/modal"
import moment from "moment"

export default {
  name: 'App',
  components: {

    // typography
    PageTitle,
    SectionTitle,
    WebLink,
    TextContent,
    VueMe,
    NLabel,

    // buttons
    NButton,
    ButtonGroup,

    // tables
    VueRawTable,
    TableRow,
    TableHeader,
    TableCell,
    TableCarat,

    // misc
    Paginator,
    List,
    ListItem,
    Modal,

    // input options
    Checkbox,
    VueInput,
    SelectMe,
    DatePicker,
    NumberRange
  },
  data() {
    return {
      graphs: [],
      selectedItem: {
        sources: []
      },
      // these toggle the sidebars and modalId
      modalId: "sourceModal",
      showFilters: false,
      showTableConfiguration: false,

      inFlight: false,


      // these provide the options for the select-me filters
      stateOptions: [],
      eventTypeOptions: [],

      // these set the limits for the number ranges
      numberRanges: [
        {filter: 'estimate_low', label: "Attendance Low (Est.)"},
        {filter: 'estimate_best', label: "Attendance Best Guess (Est.)"},
        {filter: 'estimate_high', label: "Attendance High (Est.)"},
        {filter: 'adjusted_low', label: "Adjusted Low"},
        {filter: 'adjusted_high', label: "Adjusted High"},
        {filter: 'reported_arrests', label: "Reported Arrests"},
        {filter: 'reported_participant_injuries', label: "Reported Participant Injuries"},
        {filter: 'reported_police_injuries', label: "Reported Police Injuries"},
        {filter: 'reported_property_damage', label: "Reported Property Damage"},
      ],
      defaultLimits: {
        
      },

      // these are two way bound to the various filters
      filters: {
        city__icontains: "",
        location__icontains: "",
        county__icontains: "",
        actor__icontains: "",
        claim__icontains: "",
        state__in: [],
        event_type__in: [],
        date__gte: "",
        date__lte: "",
      },

      // these control what is shown in the table
      headers: [],
      shownHeaders: [],
      items: [],

      // these are for querying items
      order_by: "-date",
      pagination: {
        pageSize: 50,
        numPages: 0,
        currentPage: 1,
        total: 0,
        start: 0,
        end: 0
      }
    }
  },
  mounted() {
    this.retrieveConfig();
    this.retrieveItems();
    console.log(this)
  },
  computed: {
    formattedFilters() {
      let default_filters = {
        page_size: this.pagination.pageSize,
        order_by: this.order_by,
        page: this.pagination.currentPage
      }
      const self = this;
      Object.keys(self.filters).forEach(key => {
        if (typeof self.filters[key] == 'string' && self.filters[key] != '') {
          default_filters[key] = self.filters[key]
        }
        else if (Array.isArray(self.filters[key]) && self.filters[key].length > 0) {
          default_filters[key] = self.filters[key].map(x => x.value)
        }
        else if (typeof self.filters[key].lowerValue !== 'undefined') {
          if (self.filters[key].lowerValue != self.defaultLimits[key].min && self.filters[key].upperValue != self.defaultLimits[key].max) {
            default_filters[`${key}__gte`] = self.filters[key].lowerValue
            default_filters[`${key}__lte`] = self.filters[key].upperValue
          }
        }
        else if (moment.isMoment(self.filters[key])) {
          default_filters[key] = self.filters[key].format("YYYY-MM-DD")
        }
      });
      return default_filters;
    }
  },
  methods: {
    handleCheckboxClick(header) {
      if (this.shownHeaders.map(h => h.value).indexOf(header.value) != -1) {
        this.shownHeaders = this.shownHeaders.filter(h => h.value != header.value)
      }
      else {
        this.shownHeaders.push(header)
      }
    },
    fetchMinMax(filter, minMax) {
      return this.defaultLimits?.[filter]?.[minMax] ?? 0
    },
    changeMinMax(filter, value) {
      if (value.lowerValue == 0 && value.upperValue == 0) {
        // values are still loading, don't update.
        return false;
      }
      this.filters[filter].lowerValue = value.lowerValue;
      this.filters[filter].upperValue = value.upperValue;
    },
    clearFilters() {
      const self = this;
      Object.keys(self.filters).forEach(key => {
        if (typeof self.filters[key] == 'string') {
          self.filters[key] = ''
        }
        else if (Array.isArray(self.filters[key])) {
          self.filters[key] = []
        }
        else if (typeof self.filters[key].lowerValue !== 'undefined') {
          this.$set(self.filters, key, {
            lowerValue: self.defaultLimits[key].min,
            upperValue: self.defaultLimits[key].max
          })
        }
        else {
          self.filters[key] = ''
        }
      });
      this.retrieveItems();
    },
    openModal(item) {
        this.selectedItem = item;
        let evt = new CustomEvent(`modal-${this.modalId}`, { detail: { "modal": true } });
        window.dispatchEvent(evt)
    },
    closeModal() {
        let evt = new CustomEvent(`modal-${this.modalId}`, { detail: { "modal": false } });
        window.dispatchEvent(evt)
    },
    handleSelect: function(page) {
        this.pagination.currentPage = page;
        this.retrieveItems()
    },
    formatValue(value) {
      if (value == null) {
        return ""
      }
      return value
    },
    setOrder(value) {
      if (this.order_by.indexOf(value) != -1) {
        if (this.order_by.indexOf("-") != -1) {
          this.order_by = value;
        }
        else {
          this.order_by = `-${value}`
        }
      }
      else {
        this.order_by = `-${value}`
      }
      this.retrieveItems();
    },

    /**
     * @function retrieveConfig
     * Retrieves the headers for the table, the state options
     * for the SelectMe filter and graphs, the event type options for the
     * SelectMe filter, the min and max values for attendance
     */
    retrieveConfig() {
      const self = this;
      axios.get("/api/config").then(response => {
        self.headers = response.data.headers;
        self.shownHeaders = response.data.headers.slice(0,5);
        self.stateOptions = response.data.stateOptions.map(state => {return {text: state, value: state}});
        self.eventTypeOptions = response.data.eventTypeOptions.map(event => {return {text: event, value: event}});

        // set mins and maxes for the number ranges
        // estimate low
        self.numberRanges.forEach(numberrange => {
          self.defaultLimits[numberrange.filter] = {
            min: response.data[`${numberrange.filter}_min`],
            max: response.data[`${numberrange.filter}_max`]
          },
          self.filters[numberrange.filter] = {
            lowerValue: response.data[`${numberrange.filter}_min`],
            upperValue: response.data[`${numberrange.filter}_max`],
          }
        })
      }).catch(() => {
        self.$alert({
          flavor: "Danger",
          title: "Error",
          content: "An error occurred while initializing the frontend.",
          buttons: [
            {
              text: "Ok",
              flavor: "Light"
            }
          ]
        })
      })
    },
    retrieveItems() {
      const self = this;
      self.inFlight = true;
      axios.get("/api/data-points", {params: self.formattedFilters}).then(response => {
        self.items = response.data.data;
        self.pagination.pageSize = response.data.page_size;
        self.pagination.numPages = response.data.num_pages;
        self.pagination.currentPage = parseInt(response.data.page);
        self.pagination.total = response.data.total;
        self.pagination.start = response.data.start;
        self.pagination.end = response.data.end;
        self.inFlight = false;
      }).catch(error => {
        self.inFlight = false;
        self.$alert({
          flavor: "Danger",
          title: "Something happened",
          content: `<div class="info-alert">${error.response.data.data}</div>`,
          buttons: [
            {
              text: "Ok",
              flavor: "Light"
            }
          ]
        })
      })
    },
    showWhatThis() {
      this.$alert({
        flavor: "Info",
        title: "What's this?",
        content: `
        <div class="info-alert">This is a data visualizer for BLM protests in the US, quickly hacked together by Pedro Del Moral Lopez</div>`,
        buttons: [
          {
            text: "Close",
            flavor: "Light"
          }
        ]
      })
    }
  }
}
</script>

<style lang="scss">
div.grapharea {
  min-height: 500px;
  display: flex;
  flex-wrap: wrap;
  &--empty {
    border: 1px dashed #636e72;
    display: flex;
    text-align: center;
    justify-content: center;
    padding: 2em;
    align-items: center;
    background-color: #f3f3f3;
    position: relative;
    height: 500px;
    flex: 1;
    &::after {
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      content: "";
      border-radius: 5px;
      border: 1em solid white;
    }
  }
}
ul.source-list {
  white-space: break-spaces;
  word-break: break-all;
  & li {
    padding: 0 1em;
  }
}
div.buttoncontainer {
  display: flex;
  flex: 1;
  padding: .5em 0;
  flex-wrap: wrap;
  align-items: center;
  .pagination-info {
    margin-left: .5em;
  }
  .pagination-controls {
    display: flex;
    align-items: center;
  }
  & > button {
    max-width: 200px;
    flex: 1;
    margin: 0 .5em;
    height: 40px;
  }
  & > button:first-of-type {
    margin-left: 0;
  }
  @media screen and (max-width: 956px){
    & .pagination-controls {
      margin: 0 auto;
    }
    & > button {
      min-width: 100%;
      margin: .25em 0;
    }
  }
}
div.container {
    max-width: 1200px;
    margin: 0 auto;
    .tablecarat {
      margin-left: .5em
    }
    .table {
      width: 100%;
      &--loading {
        text-align: center;
      }
      &__header {
        color: white;
        text-decoration: none;
      }
    }
    overflow-x: auto;
}
body {
  margin: 0;
  min-height: 100vh;
}
#app {
  position: relative;
  display: flex;
  min-height: 100vh;
  flex-direction: column;;
}
.info-alert {
  max-width: 350px;
}
footer.footer {
  background-color: #dfe6e9;
  padding: 2em 2em;
  display: flex;
  flex-direction: column;
  justify-self: flex-end;
}
div.maincontent {
  flex: 1;
  padding: 2em;
}
div.filters {
  &__title {
    & h2 {
      color: white;
      margin-right: 1em;
    }
    & > button {
      margin: .25em 0;
    }
  }
  & > div {
    margin-bottom: 1em;
  }
  &__buttongroup {
    display: flex;
    width: 100%;
    margin-bottom: 1em;
    & > button {
      flex: 1;
      height: 30px;
    }
  }
  label {
    color: white;
    font-size: 16px;
  }
  position: absolute;
  top: 60;
  left: 0px;;
  box-sizing: border-box;
  bottom: 110;
  min-height: calc(100vh -  170px);
  overflow-y:auto;
  background-color: #7595a0;
  padding: 1em;
  z-index: 2;
  width: 400px;
  transition: transform .2s;
  transform-origin: left;
  box-shadow: 3px 0px 5px rgba(0,0,0, 0.4);
  &--closed {
    transform: scaleX(0);
  }
}
div.tableconfiguration {
  &__title {
    & h2 {
      color: white;
      margin-right: 1em;
    }
  }
  li {
    list-style: none;
    padding: .25em 0;
  }
  ul {
    padding-block-start: 0;
    padding-inline-start: 0;
  }
  label {
    color: white;
    font-size: 16px;
  }
  position: absolute;
  top: 60;
  left: 0px;;
  box-sizing: border-box;
  bottom: 110;
  min-height: calc(100vh -  170px);
  overflow-y:auto;
  background-color: #7595a0;
  padding: 1em;
  z-index: 1;
  width: 350px;
  transition: transform .2s;
  transform-origin: left;
  box-shadow: 3px 0px 5px rgba(0,0,0, 0.4);
  &--closed {
    transform: scaleX(0);
  }
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0,0,0,0);
  border: 0;
}

nav.navbar {
  background-color: #636e72;
  display: flex;
  padding: 1em 2em;
  justify-content: space-between;
  h1 {
    margin-bottom: 0;
  }
  a {
    text-decoration: none;
  }
}
</style>
