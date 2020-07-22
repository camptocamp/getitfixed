document.addEventListener('DOMContentLoaded', () => {
  let geometry_oid = issue.geometry_oid

  if (!geometry_oid) { return }

  let validationFail = issue['validationFail']
  let params = new URL(window.location).searchParams
  let [x, y, z] = ['x', 'y', 'z'].map(_ => params.get(_))

  const getSelectedText = el => {
    const sel = el.querySelector('select')
    return sel.options[sel.selectedIndex].text
  }

  const typeEl = document.querySelector(`[class~=item-type_id]`)
  const catEl = document.querySelector(`[class~=item-category_id]`)
  const [catInput, typeInput] = [catEl, typeEl].map(el => el.querySelector('select'))

  // Update categories/types on moveend
  let controller
  let catId, typeId
  let map, layer
  let categories

  // Build <option> element from config obj
  const buildOption = (obj, selected) => {
    const option = document.createElement('option')
    option.value = obj.id
    if (obj.wms_layer) {
      option.setAttribute('data-wms', obj.wms_layer)
    }
    option.innerText = obj.label
    if (obj.id == selected) option.selected = 'selected'
    return option
  }

  // store selected values
  catId = parseInt(catInput.value, 10)
  typeId = parseInt(typeInput.value, 10)
  catInput.innerHTML = ''

  catInput.addEventListener('change', () => {
    // store selected value
    if (typeInput.value !== '') {
      typeId = parseInt(typeInput.value, 10)
    }

    // Update options
    const types = categories.find(e => e.id == parseInt(catInput.value, 10))?.types || []
    typeInput.innerHTML = ''
    types.forEach(o => typeInput.appendChild(buildOption(o, typeId)))

    // Autoselect first if no one selected
    if (!Array.from(typeInput.options).find(x => x.selected) && typeInput.options.length > 0) {
      typeInput.options[0].selected = 'selected'
    }
    typeInput.dispatchEvent(new Event('change', { bubbles: true }))
  })

  // Fetch categories & update form fields
  const updateCategories = () => {
    if (controller) { controller.abort() }
    controller = new AbortController()
    fetch(issue.categories_url, { signal: controller.signal })
      .then(r => r.json())
      .then(cats => {

        const _ = JSON.stringify
        if (_(cats.map(c => c.id)) == _(Array.from(catInput.options).map(n => parseInt(n.value, 10)))) {
          // Identical possible values
          return
        }

        // Store categories
        categories = cats

        // store selected values
        if (catInput.value !== '') {
          catId = parseInt(catInput.value, 10)
        }

        // Empty categories list
        catInput.innerHTML = ''
        // Fill & restore values if possible
        cats.forEach(c => catInput.appendChild(buildOption(c, catId)))
        // Autoselect first if no one selected
        if (!Array.from(catInput.options).find(x => x.selected) && catInput.options.length > 0) {
          catInput.options[0].selected = 'selected'
          catInput.dispatchEvent(new Event('change', { bubbles: true }))
        } else {
          catInput.dispatchEvent(new Event('change', { bubbles: true }))
        }
      })
      .catch(err => {
        if (err.name === 'AbortError') {
          console.log('Fetch aborted');
        } else {
          console.error(err);
        }
      })
  }
  document.querySelector(`#${geometry_oid}`).addEventListener('input', updateCategories)
  updateCategories()

  typeInput.addEventListener('change', () => {
    if (!typeInput.value || typeId === parseInt(typeInput.value, 10)) { return } // Avoid flickering

    //store type value
    typeId = parseInt(typeInput.value, 10)

    // Update WMS layer in map
    if (layer) {
      map.removeLayer(layer)
      layer = undefined
    }
    let option = typeInput.options[typeInput.selectedIndex]
    if (!option.getAttribute('data-wms')) return
    layer = c2cgeoform.addLayer(geometry_oid, {
      type_: 'WMS',
      url: option.getAttribute('data-wms')
    })
  })

  deform.addCallback(geometry_oid, function () {
    // Recenter on feature or query params
    map = c2cgeoform.getObjectMap(geometry_oid)
    let features = map.getLayers().getArray().find(l => l.getSource().getFeatures)
      .getSource().getFeatures()
    if (features.length === 0) {
      if (x && y && z) {
        map.getView().setCenter([params.get('x'), params.get('y')].map(parseFloat))
        map.getView().setZoom(parseFloat(params.get('z')))
      }
    } else {
      map.getView().fit(features[0].getGeometry().getExtent(), {
        maxZoom: 18
      })
    }

    if (!window.matchMedia('(max-width: 576px)').matches || validationFail) { return }

    // On mobile move geometry/cat/type on a temporary focused subform
    document.body.classList.add('focused')
    window.scrollTo(0, 0)
    let focus = document.querySelector('.focus')
    let mapEl = document.querySelector(`#item-${geometry_oid}`)
    focus.append(mapEl)

    let subform = document.querySelector('.subform')
    let fieldset = document.querySelector('fieldset')
    subform.prepend(typeEl)
    subform.prepend(catEl)
    map.updateSize()

    // When validating subform, move back inputs into the form,
    // turning those 3 fields read-only
    focus.querySelector('.next').addEventListener('click', () => {
      document.body.classList.remove('focused')
      ;[typeEl, catEl, mapEl].forEach(e => (fieldset.prepend(e)))
      c2cgeoform.setReadOnly(geometry_oid)
      mapEl.querySelector('label').innerText = getSelectedText(catEl) + ' / ' + getSelectedText(typeEl)
      ;[typeEl, catEl, focus].forEach(e => {e.style.display = 'none'})
      mapEl.scrollIntoView({ behavior: 'smooth' })
    })
  })
})
