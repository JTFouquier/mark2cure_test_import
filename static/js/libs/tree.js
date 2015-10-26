/*
 *  Models & Collections
 */
Relation = Backbone.RelationalModel.extend({
  defaults: {
    id: '',
    text: '',
    selected: false
  },

  relations: [{
    type: 'HasMany',
    key: 'children',

    relatedModel: 'Relation',
    collectionType: 'RelationList',

    reverseRelation : {
      key : 'parentRelation',
      includeInJSON: false,
    }
  }],

  get_selected: function() {
    /* Try to find an instance of 'this' model type in the store */
    var model = Backbone.Relational.store.find( this, {"selected": true});
    console.log('model:', model);

    if ( !model && _.isObject( attributes ) ) {
      var coll = Backbone.Relational.store.getCollection( this );

      model = coll.find( function( m ) {
        return m.selected === true;
      });
    }
    return model;
  }

});

RelationList = Backbone.Collection.extend({
  model: Relation,
  url: '/api/v1/words',
});


/*
 * Views
 */
RelationView = Backbone.Marionette.ItemView.extend({
  template: _.template('<%= text %>'),
  tagName: 'a',
  className: 'list-group-item',

  events : {
    'mousedown' : 'mousedown',
  },

  /*
  findPersonInPeopleCollection: function(nameWeAreLookingFor) {
    var model = this.model;

    function findChildren(obj) {
      if (!obj.children) return [obj];
      var children = _.map(obj.children, function(child) {
        foundPeople.push( findChildren(child) );
      });
      return _.flatten(children);
    }

    var allPeople = _.flatten( model.collection.map(findChildren) );

    return _(allPeople).find(function(obj) {
      return obj.get('selected') == true;
    }
  },
  */

  mousedown : function(evt) {
    /*
     * 1. Set the current choice to the ID
     * 2. Set the backbutton reference if available
     * 3. Set the list updated to any children
     *
     */
    var children = this.model.get('children');
    Tree['convoChannel'].trigger('click', {'collection': children, 'choice': this.model});
  },
});


RelationCompositeView = Backbone.Marionette.CompositeView.extend({
  template: '#tree-template',
  templateHelpers: function() {
    return this.options.concepts
  },

  childView  : RelationView,
  childViewContainer: "ul",
  /*
  tagName   : 'div',
  className : 'paragraph',
  */

  ui: {
    'c1': '#c1',
    'relation': '#relation',
    'c2': '#c2',
  },

  events : {
    'mousedown @ui.relation': 'resetRelationship'
  },

  resetRelationship: function(evt) {
    Tree['convoChannel'].trigger('back', this.options);
  },

  onRender : function() {
    var self = this;
    var choice = this.options['choice'];
    var concepts = this.options['concepts'];
    /*
     * console.log('[RelationCompositeView onRender] Choice:', choice);
     */

    if(choice) {
      this.ui.relation.removeClass('disabled').text( choice.get('text') );
    }

    if(choice || this.collection.parentRelation) {
      this.ui.relation.removeClass('disabled');
      self.ui.relation.addClass('relation-go-back');
    }

    var c1TimeoutId;
    this.ui.c1.hover(function() {
      if (!c1TimeoutId) {
        c1TimeoutId = window.setTimeout(function() {
          c1TimeoutId = null;
          self.ui['c1'].addClass('not-correct-concept');
          self.ui['c1'].html('<h3>Is '+ concepts['c1'].text + ' not a '+ concepts['c1'].type +'?</h3>');
        }, 500);
      }
    }, function() {
      if (c1TimeoutId) {
        window.clearTimeout(c1TimeoutId);
        c1TimeoutId = null;
        self.render();
      } else {
        console.log('elsed');
        self.render();
      }
    });

    var c2TimeoutId;
    this.ui.c2.hover(function() {
      if (!c2TimeoutId) {
        c2TimeoutId = window.setTimeout(function() {
          c2TimeoutId = null;
          self.ui['c2'].addClass('not-correct-concept');
          self.ui['c2'].html('<h3>Is '+ concepts['c2'].text + ' not a '+ concepts['c2'].type +'?</h3>');
        }, 750);
      }
    }, function() {
      if (c2TimeoutId) {
        window.clearTimeout(c2TimeoutId);
        c2TimeoutId = null;
        self.render();
      } else {
        console.log('elsed');
        self.render();
      }
    });

  }
});

Tree = new Backbone.Marionette.Application();