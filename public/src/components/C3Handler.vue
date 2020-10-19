<template>
  <div class="c3-container">
    <vue-c3 :handler="handler"></vue-c3>
  </div>
</template>

<script>
import Vue from "vue";
import VueC3 from "vue-c3";

/**
 * Controls the C3 graph
 */
export const C3Handler = {
  components: {
    VueC3,
  },
  props: {
    data: { Object },
  },
  beforeDestroy() {
    this.handler.$emit("destroy");
  },
  watch: {
    /**
     * options configure the chart. If they change, we destroy the chart and reinitialize it rather than figuring
     * out what changed and updating the chart. Less performant, but easier to manage
     */
    data: {
      handler() {
        this.handler.$emit("destroy");
        this.handler.$emit("init", this.options);
      },
      deep: true,
    },
  },
  methods: {
    /**
     * Formats data in the format expected by C3js to display a line chart
     */
    // lineChartData() {
    //   let c3Data = {
    //     ...this.c3Data,
    //     data: {
    //       x: "x",
    //       columns: [],
    //       labels: true,
    //     },
    //     axis: {
    //       x: {
    //         type: "category",
    //       },
    //     },
    //   };
    //   if (this.graphedFieldDetails.graph_type == "line") {
    //     // graphedField is the y values, qualifications the x values
    //     let field = this.graphedField[0].value;
    //     // so far only qualified fields are line charts
    //     if (this.graphedFieldDetails.type == "Qualified") {
    //       let xAxis = ["x"];
    //       let yAxis = [];
    //       // grab the qualifications
    //       let qualifications = Object.keys(
    //         this.graphedFieldDetails.values
    //       ).filter((x) => this.ignoredFields.indexOf(x) == -1);
    //       for (let key of qualifications) {
    //         xAxis.push(key);
    //       }
    //       for (let item of this.selectedItems) {
    //         // start a data series for each selected item
    //         let dataSeries = [item.primary_designator.value];
    //         // grab the details for the item
    //         let detailedItem = this.details[item.id];
    //         // grab the qualifications we care about
    //         let itemQualifications = Object.keys(
    //           detailedItem[field].values
    //         ).filter((x) => this.ignoredFields.indexOf(x) == -1);
    //         // add the data for each qualification to the data series
    //         for (let qualification of itemQualifications) {
    //           dataSeries.push(detailedItem[field].values[qualification].value);
    //         }
    //         yAxis.push(dataSeries);
    //       }
    //       c3Data.data.columns = [xAxis, ...yAxis];
    //     }
    //   }
    //   return c3Data;
    // },
    /**
     * When two fields are selected, we graph a cross chart (scatter plot).
     * We format the data in the format expected by C3JS.
     */
    // crossChartData() {
    //   let self = this;
    //   let c3Data = {
    //     ...this.c3Data,
    //     data: {
    //       xs: {},
    //       type: "scatter",
    //       labels: {
    //         format: {},
    //       },
    //     },
    //     axis: {
    //       x: {
    //         label: { position: "outer-center" },
    //         tick: {
    //           fit: false,
    //         },
    //       },
    //       y: {
    //         label: { position: "outer-middle" },
    //         tick: {
    //           fit: false,
    //         },
    //       },
    //     },
    //   };
    //   let fieldSection = `${this.graphedField[0].text}`;
    //   let crossFieldSection = `${this.crossGraphedField[0].text}`;
    //   /**
    //    * x: Field
    //    * y: crossField
    //    */
    //   c3Data.axis.x.label.text = ""; // TODO SET LABEL TO FIRST FIELD
    //   c3Data.axis.y.label.text = ""; // TODO SET LABLE TO SECOND FIELD
    //   c3Data.data.columns = [];
    //   let index = 0;
    //   let columnIndex = 0;
    //   for (let selectedItem of this.selectedItems) {
    //     // the x values for this selectedItem
    //     c3Data.data.columns.push([`${TODO_GET_FIELD}_x`]);
    //     // the y values for this system. We use the designator to map the y to the x in c3js
    //     c3Data.data.columns.push([TODO_GET_FIELD]);
    //     // set the y values to use the _x data series as x values. Otherwise c3js defaults to
    //     // "data series index" for X values
    //     c3Data.data.xs[TODO_GET_FIELD] = `${TODO_GET_FIELD}_x`;
    //     let detailedItem = this.detailedItems[index];
    //     // x coordinate values
    //     c3Data.data.columns[columnIndex].push(TODO_GET_X_DATA);
    //     // y coordinate values
    //     c3Data.data.columns[columnIndex + 1].push(TODO_GET_Y_DATA);
    //     index++;
    //     columnIndex += 2;
    //   }
    //   return c3Data;
    // },
    /**
     * Formats data in the format expected by C3JS to display a bar chart
     */
    // barChartData() {
    //   let self = this;
    //   let c3Data = {
    //     ...this.c3Data,
    //     data: {
    //       x: "x",
    //       columns: [],
    //       type: "bar",
    //       labels: true,
    //       colors: this.c3Colors,
    //       color: function(color, d) {
    //         if (typeof d == "string") {
    //           return;
    //         }
    //         return self.c3Colors[
    //           self.selectedItems[d.index].primary_designator.value
    //         ];
    //       },
    //     },
    //     axis: {
    //       rotated: true,
    //       x: {
    //         type: "category",
    //       },
    //     },
    //     grid: {
    //       y: {
    //         show: true,
    //       },
    //     },
    //   };
    //   if (this.graphedFieldDetails.graph_type == "bar") {
    //     let field = this.graphedField[0].value;
    //     // currently only regular fields are graphed as bar charts
    //     if (this.graphedFieldDetails.type == "regular") {
    //       let xAxis = ["x"];
    //       let yAxis = [field];
    //       // xAxis is the primary designator
    //       for (let item of this.selectedItems) {
    //         xAxis.push(item.primary_designator.value);
    //         let yVal = this.details[item.id][field];
    //         if (typeof yVal != "undefined") {
    //           yAxis.push(yVal.value);
    //         } else {
    //           yAxis.push(0);
    //         }
    //       }
    //       c3Data.data.columns = [xAxis, yAxis];
    //     }
    //   }
    //   return c3Data;
    // },
    /**
     * Formats data in the format expected by C3JS to display a scatter chart
     */
    // scatterChartData() {
    //   let c3Data = {
    //     ...this.c3Data,
    //     data: {
    //       type: "scatter",
    //       x: "x",
    //       columns: [],
    //       labels: true,
    //       colors: this.c3Colors,
    //     },
    //     axis: {
    //       x: {
    //         type: "category",
    //         tick: {
    //           fit: false,
    //         },
    //       },
    //       y: {
    //         tick: {
    //           fit: false,
    //         },
    //       },
    //     },
    //   };
    //   if (this.graphedFieldDetails.graph_type == "scatter") {
    //     let field = this.graphedField[0].value;
    //     // currently only Number3 fields are scatter charts
    //     if (this.graphedFieldDetails.type == "Number3") {
    //       let xAxis = ["x"];
    //       // we can hard code what the X Axis is, just check to see if the values exist, and add it if it does
    //       if (typeof this.graphedFieldDetails["Lower Limit"] != "undefined") {
    //         xAxis.push("Lower");
    //       }
    //       // we can hard code what the X Axis is, just check to see if the values exist, and add it if it does
    //       if (typeof this.graphedFieldDetails["Nominal Value"] != "undefined") {
    //         xAxis.push("Nominal");
    //       }
    //       // we can hard code what the X Axis is, just check to see if the values exist, and add it if it does
    //       if (typeof this.graphedFieldDetails["Upper Limit"] != "undefined") {
    //         xAxis.push("Upper");
    //       }
    //       let yAxis = [];
    //       for (let item of this.selectedItems) {
    //         let dataSeries = [item.primary_designator.value];
    //         let detailedItem = this.details[item.id];
    //         if (typeof detailedItem[field]["Lower Limit"] !== "undefined") {
    //           dataSeries.push(detailedItem[field]["Lower Limit"].value);
    //         }
    //         if (typeof detailedItem[field]["Nominal Value"] !== "undefined") {
    //           dataSeries.push(detailedItem[field]["Nominal Value"].value);
    //         }
    //         if (typeof detailedItem[field]["Upper Limit"] !== "undefined") {
    //           dataSeries.push(detailedItem[field]["Upper Limit"].value);
    //         }
    //         yAxis.push(dataSeries);
    //       }
    //       c3Data.data.columns = [xAxis, ...yAxis];
    //     }
    //   }
    //   return c3Data;
    // },
  },
  mounted() {
    this.handler.$emit("init", this.options);
  },
  computed: {
    options() {
      if (this.data.fieldY) {
        // cross graph
      } else {
        if (this.data.fieldX == "date") {
          // special case, line graph
        } else if (this.data.fieldX == "state") {
          // special case, map
        } else if (this.bar) {
          // display as bar graph
          const self = this;
          let columns = [];
          self.data.dataX.forEach((dataset) => {
            let subColumn = [];
            Object.keys(dataset).forEach((key) => {
              subColumn.push(dataset[key]);
            });
            columns.push(subColumn);
          });
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: columns,
              type: "bar",
            },
          };
          console.log(c3Data);
          return c3Data;
        } else {
          // display as pie chart
        }
      }
    },
  },
  data() {
    return {
      handler: new Vue(),
      bar: true,
      c3Data: {
        point: {
          r: 4,
        },
        size: {
          height: 400,
        },
        padding: {
          top: 10,
          left: 100,
          right: 100,
        },
        legend: {
          hide: true,
        },
      },
    };
  },
};
export default C3Handler;
</script>

<style lang="scss">
.c3-container {
  max-width: 50%;
  flex: 1;
  &--maxed {
    max-width: 100%;
  }
}
.c3-tooltip-container {
  z-index: 3;
  background-color: #efefef;
  padding: 1em;
  max-height: 400px;
  border-radius: 5px;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.4);
  overflow-y: auto;
}
.c3-container * {
  font-family: "Open Sans Regular", -apple-system, BlinkMacSystemFont, Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
}
</style>
