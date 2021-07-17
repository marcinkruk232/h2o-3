package water.api;

import hex.Model;
import hex.ModelBuilder;
import water.Job;
import water.Key;
import water.api.schemas.InfoGramV99;
import water.util.Log;

import java.util.Properties;

public class InfoGramBuilderHandler extends Handler {
  @Override
  public InfoGramV99 handle(int version, water.api.Route route, Properties parms, String postBody) throws Exception {
    final String methodName = route._handler_method.getName();
    if ("train".equals(methodName)) {
      return buildInfoGram(parms);
    } else {
      throw water.H2O.unimpl();
    }
  }
  
  private InfoGramV99 buildInfoGram(Properties parms) {
    InfoGramV99 infoSchema = buildInfoGramSchema(parms);
    // Get/create a model_id for given frame
    String model_id = parms.getProperty("model_id");
    String warningStr = null;
    if ((model_id != null) && (model_id.contains("/"))) { // found / in model_id, replace with _ and set warning
      String tempName = model_id;
      model_id = model_id.replaceAll("/", "_");
      warningStr = "Bad model_id: slash (/) found and replaced with _.  " + "Original model_id "+tempName +
              " is now "+model_id+".";
      Log.warn("model_id", warningStr);
    }
    Key<Model> key = model_id==null ? ModelBuilder.defaultKey("InfoGram") : Key.make(model_id);
    Job job = warningStr!=null ? new Job<>(key, ModelBuilder.javaName("InfoGram"), "infogram", warningStr) :
            new Job<>(key, ModelBuilder.javaName("infogram"),"InfoGram");
    return infoSchema;
  }
  
  private InfoGramV99 buildInfoGramSchema(Properties parms) {
    InfoGramV99 infogramSchema = new InfoGramV99();
    infogramSchema.init_meta();
    infogramSchema.fillFromParms(parms);
    return infogramSchema;
  }
/*  @SuppressWarnings("unused") // called through reflection by RequestServer
  public InfoGramV99 build(int version, InfoGramV99 schema) {

  }*/
}
