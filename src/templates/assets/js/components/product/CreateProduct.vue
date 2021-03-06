<template>
  <section>
    <div class="row">
      <div class="col-md-6">
        <div class="card shadow mb-4">
          <div class="card-body">
            <div class="form-group">
              <label for="">Product Name</label>
              <input type="hidden" v-model="product_id">
              <input type="text" v-model="product_name" placeholder="Product Name" class="form-control">
            </div>
            <div class="form-group">
              <label for="">Product SKU</label>
              <input type="text" v-model="product_sku" placeholder="Product Name" class="form-control">
            </div>
            <div class="form-group">
              <label for="">Description</label>
              <textarea v-model="description" id="" cols="30" rows="4" class="form-control"></textarea>
            </div>
          </div>
        </div>

        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Media</h6>
          </div>
          <div class="card-body border">
            <vue-dropzone ref="myVueDropzone" id="dropzone" :options="dropzoneOptions"></vue-dropzone>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Variants</h6>
          </div>
          <div class="card-body">
            <div class="row" v-for="(item,index) in product_variant">
              <div class="col-md-4">
                <div class="form-group">
                  <label for="">Option</label>
                  <select v-model="item.option" class="form-control">
                    <option v-for="variant in variants"
                            :value="variant.id">
                      {{ variant.title }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-8">
                <div class="form-group">
                  <label v-if="product_variant.length != 1" @click="product_variant.splice(index,1); checkVariant"
                         class="float-right text-primary"
                         style="cursor: pointer;">Remove</label>
                  <label v-else for="">.</label>
                  <input-tag v-model="item.tags" @input="checkVariant" class="form-control"></input-tag>
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer" v-if="product_variant.length < variants.length && product_variant.length < 3">
            <button @click="newVariant" class="btn btn-primary">Add another option</button>
          </div>

          <div class="card-header text-uppercase">Preview</div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table">
                <thead>
                <tr>
                  <td>Variant</td>
                  <td>Price</td>
                  <td>Stock</td>
                </tr>
                </thead>
                <tbody>
                <tr v-for="variant_price in product_variant_prices">
                  <td>{{ variant_price.title }}</td>
                  <td>
                    <input type="text" class="form-control" v-model="variant_price.price">
                  </td>
                  <td>
                    <input type="text" class="form-control" v-model="variant_price.stock">
                  </td>
                </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    <button v-if="product_id" @click="updateProduct" type="submit" class="btn btn-lg btn-primary">Update</button>
    <button v-else @click="saveProduct" type="submit" class="btn btn-lg btn-primary">Save</button>
    <button type="button" class="btn btn-secondary btn-lg">Cancel</button>
  </section>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import InputTag from 'vue-input-tag'
import axios from 'axios'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";
//axios.defaults.headers.post['Content-Type'] = 'multipart/form-data';


export default {
  components: {
    vueDropzone: vue2Dropzone,
    InputTag
  },
  props: {
    variants: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      product_id : '',
      product_name: '',
      product_sku: '',
      description: '',
      images: [],
      product_variant: [
        {
          option: this.variants[0].id,
          tags: []
        }
      ],
      product_variant_prices: [],
      dropzoneOptions: {
        url: 'https://httpbin.org/post',
        thumbnailWidth: 150,
        maxFilesize: 0.5,
        headers: {"My-Awesome-Header": "header value"}
      }
    }
  },
  methods: {
    // it will push a new object into product variant
    newVariant() {
      let all_variants = this.variants.map(el => el.id)
      let selected_variants = this.product_variant.map(el => el.option);
      let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
      // console.log(available_variants)

      this.product_variant.push({
        option: available_variants[0],
        tags: []
      })
    },

    // check the variant and render all the combination
    checkVariant() {
      let tags = [];
      this.product_variant_prices = [];
      this.product_variant.filter((item) => {
        tags.push(item.tags);
      })

      this.getCombn(tags).forEach(item => {
        this.product_variant_prices.push({
          title: item,
          price: 0,
          stock: 0
        })
      })
    },

    // combination algorithm
    getCombn(arr, pre) {
      pre = pre || '';
      if (!arr.length) {
        return pre;
      }
      let self = this;
      let ans = arr[0].reduce(function (ans, value) {
        return ans.concat(self.getCombn(arr.slice(1), pre + value + '/'));
      }, []);
      return ans;
    },

    // store product into database
    saveProduct() {
      let product = {
        title: this.product_name,
        sku: this.product_sku,
        description: this.description,
        product_image: this.images,
        product_variant: this.product_variant,
        product_variant_prices: this.product_variant_prices
      }
      
      axios.post('/product/create/', product).then(response => {
        if(response.data === 1) {
          window.alert("Product Saved");
        }
      }).catch(error => {
        console.log(error);
      })

      console.log(product);
    },
    updateProduct() {
      let product = {
        id: this.product_id,
        title: this.product_name,
        sku: this.product_sku,
        description: this.description,
        product_image: this.images,
        product_variant: this.product_variant,
        product_variant_prices: this.product_variant_prices
      }
      
      axios.post(`/product/${product.id}/edit`, product).then(response => {
        if(response.data === 1) {
          window.alert("Product Updated");
        }
      }).catch(error => {
        console.log(error);
      })

      console.log(product);
    }


  },
  mounted() {
    if (document.getElementById("product").textContent.length) {
      var product = JSON.parse(document.getElementById('product').textContent);
      var product_variants = JSON.parse(document.getElementById('product_variants').textContent);
      var product_variant_prices = JSON.parse(document.getElementById('product_variant_prices').textContent);
      var product_variant = [];
      var tag_dict = {};
      for (var i = 0; i < product_variants.length; i++) {
        var pv = product_variants[i];
        if (!tag_dict[pv.variant]) {
            tag_dict[pv.variant] = [];
        }
        tag_dict[pv.variant].push(pv.variant_title);
      }
      for (const [key, value] of Object.entries(tag_dict)) {
        product_variant.push({
          option: key,
          tags: value
        });
      }
      for (var i = 0; i < product_variant_prices.length; i++) {
         var item = product_variant_prices[i];
         item.title = item.product_variant_one + '/' + item.product_variant_two + '/' + item.product_variant_three  + '/';
      }
      this.product_id = product.id;
      this.product_name = product.title;
      this.product_sku = product.sku;
      this.description = product.description;
      this.product_variant = product_variant;
      this.product_variant_prices = product_variant_prices;
    }
    console.log('Component mounted.')
  }
}
</script>