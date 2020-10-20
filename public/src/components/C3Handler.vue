<template>
  <div
    class="c3-container"
    :class="{
      'hidden-axis': tooManyValues,
      'c3-container--maxed': expand,
    }"
  >
    <sub-section-title>{{ title }}</sub-section-title>
    <div class="mapbuttoncontainer">
      <n-button flavor="Danger" small @click="$emit('delete')">
        <span class="sr-only">Delete Chart</span>
        <i class="fa fa-2x fa-trash"></i>
      </n-button>
      <n-button
        flavor="Light"
        small
        title="Expand Chart"
        v-if="expand == false"
        @click="expand = true"
      >
        <span class="sr-only">Expand Chart</span>
        <i class="fa fa-2x fa-expand" aria-hidden="true"></i>
      </n-button>
      <n-button
        title="Compress Chart"
        flavor="Light"
        small
        v-else
        @click="expand = false"
      >
        <span class="sr-only">Compress Chart</span>
        <i class="fa fa-2x fa-compress" aria-hidden="true"></i>
      </n-button>
      <n-button
        flavor="Light"
        small
        v-if="showPieChart"
        title="Convert to Pie Chart"
        @click="
          bar = false;
          country = false;
        "
      >
        <span class="sr-only">Convert to Pie Chart</span>
        <i class="fa fa-pie-chart fa-2x" aria-hidden="true"></i>
      </n-button>
      <n-button
        flavor="Light"
        small
        title="Flip Axis"
        v-if="!(data.fieldX == 'state' && typeof data.fieldY == 'undefined')"
        @click="switchAxis = !switchAxis"
      >
        <span class="sr-only">Switch Axis</span>
        <i class="fa fa-2x fa-refresh"></i>
      </n-button>
      <n-button
        flavor="Light"
        title="Convert to State Heat Map"
        small
        v-if="showCountryChart"
        @click="country = true"
      >
        <span class="sr-only">Convert to Country Map</span>
        <i class="fa fa-globe fa-2x" aria-hidden="true"></i>
      </n-button>
      <n-button
        title="Convert to Bar Chart"
        flavor="Light"
        small
        v-if="showBarChart"
        @click="bar = true"
      >
        <span class="sr-only">Convert to Bar Chart</span>
        <i class="fa fa-bar-chart fa-2x" aria-hidden="true"></i>
      </n-button>
    </div>
    <state-heat-map
      :data="data"
      v-if="
        data.fieldX == 'state' && typeof data.fieldY == 'undefined' && country
      "
    ></state-heat-map>
    <vue-c3 v-else :handler="handler"></vue-c3>
  </div>
</template>

<script>
import Vue from "vue";
import VueC3 from "vue-c3";
import NButton from "@IntusFacultas/button";
import SubSectionTitle from "@IntusFacultas/typography";
import "font-awesome/css/font-awesome.min.css";
import "c3/c3.css";
import StateHeatMap from "./StateHeatMap";
/**
 * Controls the C3 graph
 */
export const C3Handler = {
  components: {
    VueC3,
    NButton,
    SubSectionTitle,
    StateHeatMap,
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
    country: {
      handler() {
        console.log("fire");
        const self = this;
        setTimeout(() => {
          self.handler.$emit("destroy");
          self.handler.$emit("init", self.options);
        }, 25);
      },
    },
    bar: {
      handler() {
        this.handler.$emit("destroy");
        this.handler.$emit("init", this.options);
      },
    },
    switchAxis: {
      handler() {
        this.handler.$emit("destroy");
        this.handler.$emit("init", this.options);
      },
    },
    expand: {
      handler() {
        const self = this;
        setTimeout(() => {
          self.handler.$emit("dispatch", (chart) => chart.resize());
        }, 25);
      },
    },
    data: {
      handler() {
        this.handler.$emit("destroy");
        this.handler.$emit("init", this.options);
      },
      deep: true,
    },
  },
  mounted() {
    this.handler.$emit("init", this.options);
  },
  computed: {
    showPieChart() {
      if (this.data.fieldY) {
        return false;
      } else if (this.data.fieldX == "state") {
        return this.country;
      }
      return this.bar;
    },
    showCountryChart() {
      if (this.data.fieldY) {
        return false;
      } else if (this.data.fieldX == "state") {
        return !this.country;
      }
    },
    showBarChart() {
      if (this.data.fieldY || this.data.fieldX == "state") {
        return false;
      }
      return !this.bar;
    },
    title() {
      let title = `Events by ${this.data.fieldXLabel}`;
      if (this.data.fieldYLabel) {
        title += ` vs # of ${this.data.fieldYLabel}`;
      }
      return title;
    },
    tooManyValues() {
      const dataYLength = this.data?.dataY?.length ?? 0;
      return this.data.dataX.length > 10 || dataYLength > 10;
    },
    options() {
      if (this.data.fieldY) {
        if (this.data.fieldX == "date") {
          // special case, line graph
          const self = this;
          let columns = [this.data.fieldYLabel];
          self.data.dataY.forEach((dataset) => {
            columns.push(dataset.y);
          });
          const reducer = (acc, val) => {
            acc.push(val.date);
            return acc;
          };
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: [columns],
            },
            axis: {
              y: {
                label: {
                  position: "outer-middle",
                  text: self.data.fieldYLabel,
                },
              },
              x: {
                label: {
                  text: self.data.fieldXLabel,
                  position: "outer-center",
                },
                type: "category",
                categories: self.data.dataY.reduce(reducer, []),
              },
            },
          };
          return c3Data;
        } else {
          const self = this;
          let columns = [self.data.fieldYLabel];
          self.data.dataY.forEach((dataset) => {
            columns.push(dataset.y);
          });
          const reducer = (acc, val) => {
            acc.push(val[self.data.fieldX]);
            return acc;
          };
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: [columns],
              type: "bar",
            },
            axis: {
              y: {
                label: {
                  position: "outer-middle",
                  text: self.data.fieldYLabel,
                },
              },
              x: {
                label: {
                  text: self.data.fieldXLabel,
                  position: "outer-center",
                },
                type: "category",
                categories: self.data.dataY.reduce(reducer, []),
              },
            },
          };
          return c3Data;
        }
      } else {
        if (this.data.fieldX == "date") {
          // special case, line graph
          const self = this;
          let columns = ["Events"];
          self.data.dataX.forEach((dataset) => {
            columns.push(dataset.count);
          });
          const reducer = (acc, val) => {
            acc.push(val[self.data.fieldX]);
            return acc;
          };
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: [columns],
            },
            axis: {
              y: {
                label: {
                  position: "outer-middle",
                  text: "Number of Events",
                },
              },
              x: {
                label: {
                  text: self.data.fieldXLabel,
                  position: "outer-center",
                },
                type: "category",
                categories: self.data.dataX.reduce(reducer, []),
              },
            },
          };
          return c3Data;
        } else if (this.data.fieldX == "state") {
          const self = this;
          let columns = [];
          self.data.dataX.forEach((dataset) => {
            columns.push([dataset[self.data.fieldX], dataset.count]);
          });
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: columns,
              type: "pie",
            },
          };
          return c3Data;
          // special case, map
        } else if (this.bar) {
          // display as bar graph
          const self = this;
          let columns = ["Events"];
          self.data.dataX.forEach((dataset) => {
            columns.push(dataset.count);
          });
          const reducer = (acc, val) => {
            acc.push(val[self.data.fieldX]);
            return acc;
          };
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: [columns],
              type: "bar",
            },
            axis: {
              y: {
                label: {
                  position: "outer-middle",
                  text: "Number of Events",
                },
              },
              x: {
                label: {
                  text: self.data.fieldXLabel,
                  position: "outer-center",
                },
                type: "category",
                categories: self.data.dataX.reduce(reducer, []),
              },
            },
          };
          return c3Data;
        } else {
          // display as pie chart
          const self = this;
          let columns = [];
          self.data.dataX.forEach((dataset) => {
            columns.push([dataset[self.data.fieldX], dataset.count]);
          });
          let c3Data = {
            ...self.c3Data,
            data: {
              columns: columns,
              type: "pie",
            },
          };
          return c3Data;
        }
      }
    },
  },
  data() {
    return {
      handler: new Vue(),
      bar: true,
      switchAxis: false,
      country: true,
      expand: false,
      c3Data: {
        point: {
          r: 4,
        },
        // legend: {
        //   hide: true,
        // },
      },
    };
  },
};
export default C3Handler;
</script>

<style lang="scss">
.hidden-axis {
  .c3-axis-x-label ~ g {
    display: none;
  }
}

.vuec3-chart * {
  font-family: "Open Sans Regular", -apple-system, BlinkMacSystemFont, Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-size: 14px;
}
.c3-tooltip-container {
  padding: 0.1em;
  border-radius: 2px;
  background-color: white;
}
.mapbuttoncontainer {
  position: absolute;
  top: 0;
  display: flex;
  & button {
    margin: 0 0.2em;
  }
  right: 0;
}
.c3-container {
  max-width: 50%;
  min-width: 50%;
  min-height: 400px;
  flex: 1;
  text-align: center;
  position: relative;
  &--maxed {
    min-width: 100%;
    max-width: 100%;
  }
  // tspan {
  //   display: none;
  // }
}
</style>
